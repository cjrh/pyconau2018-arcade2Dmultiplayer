import copy
import logging
import asyncio
import threading
import time
from collections import deque
from typing import Dict
import zmq
from zmq.asyncio import Context, Socket
import arcade
from pymunk.vec2d import Vec2d
from .lib02 import PlayerEvent, PlayerState, GameState


logger = logging.getLogger(__name__)
logger.setLevel('INFO')
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50

MOVEMENT_SPEED = 5
UPDATE_TICK = 15

MOVE_MAP = {
    arcade.key.UP: Vec2d(0, 1),
    arcade.key.DOWN: Vec2d(0, -1),
    arcade.key.LEFT: Vec2d(-1, 0),
    arcade.key.RIGHT: Vec2d(1, 0),
}


class Rectangle:
    def __init__(self, x, y, width, height, angle, color):
        self.position = Vec2d(x, y)
        self.movement: Dict[Vec2d] = {}

        # Size and rotation
        self.width = width
        self.height = height
        self.angle = angle

        # Color
        self.color = color

    def draw(self):
        arcade.draw_rectangle_filled(
            self.position.x, self.position.y,
            self.width, self.height,
            self.color, self.angle
        )


class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, title="Multiplayer Demo")
        self.player = Rectangle(
            0, 0, RECT_WIDTH, RECT_HEIGHT, 0, arcade.color.WHITE)
        self.player_event = PlayerEvent()
        self.game_state = GameState(
            player_states=[
                PlayerState()
            ],
            game_seconds=0
        )
        self.position_buffer = deque(maxlen=3)
        self.t = 0

    def setup(self):
        x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2
        self.player.position += Vec2d(x, y)

    def lerp(self, v0: float, v1: float, t: float):
        if t > 1:
            t = 1
        return (1 - t) * v0 + t * v1

    def update(self, dt):
        # TODO: actually nothing to do here (until interpolation)
        # self.player.move()
        if len(self.position_buffer) < 2:
            return

        v0, t0 = self.position_buffer[0]
        v1, t1 = self.position_buffer[1]

        if t0 == t1:
            return

        x = (self.t - t0) / (t1 - t0)
        logger.debug(f'{dt:8.4f} {x:8.3} {self.t:16.4} {t0:16.4} {t1:16.4} {t1 - t0:8.3}')

        netcode_position = self.lerp(
            self.player.position, v1, x
        )

        speed = 500
        dx = 0
        dy = 0
        if self.player_event.left:
            dx -= speed * dt
        if self.player_event.right:
            dx += speed * dt
        if self.player_event.up:
            dy += speed * dt
        if self.player_event.down:
            dy -= speed * dt

        local_position = copy.copy(self.player.position)
        local_position.x += dx
        local_position.y += dy

        # So here we have the netcode position, and the local position.
        # Let's interpolate between them!
        self.player.position.x = (netcode_position.x + local_position.x) / 2
        self.player.position.y = (netcode_position.y + local_position.y) / 2

        # self.player.position = self.lerp(
        #     self.player.position, v1, x
        # )

        self.t += dt

    def on_draw(self):
        arcade.start_render()
        self.player.draw()

    def on_key_press(self, key, modifiers):
        # self.player.movement[key] = MOVE_MAP[key] * MOVEMENT_SPEED
        logger.debug(key)
        self.player_event.left |= key == arcade.key.LEFT
        self.player_event.right |= key == arcade.key.RIGHT
        self.player_event.up |= key == arcade.key.UP
        self.player_event.down |= key == arcade.key.DOWN

    def on_key_release(self, key, modifiers):
        # del self.player.movement[key]
        self.player_event.left ^= key == arcade.key.LEFT
        self.player_event.right ^= key == arcade.key.RIGHT
        self.player_event.up ^= key == arcade.key.UP
        self.player_event.down ^= key == arcade.key.DOWN


async def thread_main(window: MyGame, loop):
    ctx = Context()

    sub_sock: Socket = ctx.socket(zmq.SUB)
    sub_sock.connect('tcp://localhost:25000')
    sub_sock.subscribe('')

    push_sock: Socket = ctx.socket(zmq.PUSH)
    push_sock.connect('tcp://localhost:25001')

    async def pusher():
        """Push the player's INPUT state 60 times per second"""
        while True:
            d = window.player_event.asdict()
            # logger.debug(d)
            await push_sock.send_json(d)
            await asyncio.sleep(1 / UPDATE_TICK)

    async def receive_game_state():
        while True:
            gs_string = await sub_sock.recv_string()
            # logger.debug('.', end='', flush=True)
            window.game_state.from_json(gs_string)
            ps = window.game_state.player_states[0]
            t = time.time()
            window.position_buffer.append(
                (Vec2d(ps.x, ps.y), t)
            )
            window.t = window.position_buffer[0][1]

    try:
        await asyncio.gather(pusher(), receive_game_state())
    finally:
        sub_sock.close(1)
        push_sock.close(1)
        ctx.destroy(linger=1)


def thread_worker(window: MyGame):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(thread_main(window, loop))
    loop.run_forever()


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()

    thread = threading.Thread(
        target=thread_worker, args=(window,), daemon=True)
    thread.start()

    arcade.run()


if __name__ == "__main__":
    main()
