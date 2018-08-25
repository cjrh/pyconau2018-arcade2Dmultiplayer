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

from demos.movement import KeysPressed, MOVE_MAP, apply_movement
from .lib02 import PlayerEvent, PlayerState, GameState

logger = logging.getLogger(__name__)
logger.setLevel('INFO')
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50

MOVEMENT_SPEED = 5
UPDATE_TICK = 30


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
        self.filled = True

    def draw(self):
        if self.filled:
            arcade.draw_rectangle_filled(
                self.position.x, self.position.y,
                self.width, self.height,
                self.color, self.angle
            )
        else:
            arcade.draw_rectangle_outline(
                self.position.x, self.position.y,
                self.width, self.height,
                self.color, border_width=4,
                tilt_angle=self.angle
            )


class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, title="Multiplayer Demo")
        self.keys_pressed = KeysPressed()
        arcade.set_background_color(arcade.color.GRAY)
        self.player = Rectangle(
            0, 0, RECT_WIDTH, RECT_HEIGHT, 0, arcade.color.GREEN_YELLOW)
        self.player_position_snapshot = copy.copy(self.player.position)
        self.player.filled = False
        self.ghost = Rectangle(
            0, 0, RECT_WIDTH, RECT_HEIGHT, 0, arcade.color.BLACK)
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
        self.ghost.position += Vec2d(x, y)

    def lerp(self, v0: float, v1: float, t: float):
        """ L-inear int-ERP-olation"""
        return (1 - t) * v0 + t * v1

    def update(self, dt):
        # Now calculate the new position based on the server information
        if len(self.position_buffer) < 2:
            return

        # These are the last two positions. p1 is the latest, p0 is the
        # one immediately preceding it.
        p0, t0 = self.position_buffer[0]
        p1, t1 = self.position_buffer[1]

        dtt = t1 - t0
        if dtt == 0:
            return

        # Calculate a PREDICTED future position, based on these two.
        velocity = (p1 - p0) / dtt

        # predicted position
        predicted_position = velocity * dtt + p1

        x = (self.t - 0) / dtt
        x = min(x, 1)
        interp_position = self.lerp(
            self.player_position_snapshot, predicted_position, x
        )

        self.player.position = interp_position
        # self.player.position = p1
        self.ghost.position = p1

        self.t += dt

    def on_draw(self):
        arcade.start_render()
        self.ghost.draw()
        self.player.draw()

    def on_key_press(self, key, modifiers):
        # self.player.movement[key] = MOVE_MAP[key] * MOVEMENT_SPEED
        logger.debug(key)
        self.player_event.keys[key] = True
        self.keys_pressed.keys[key] = True

    def on_key_release(self, key, modifiers):
        # del self.player.movement[key]
        self.player_event.keys[key] = False
        self.keys_pressed.keys[key] = False


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
            msg = dict(counter=1, event=d)
            await push_sock.send_json(msg)
            await asyncio.sleep(1 / UPDATE_TICK)

    async def receive_game_state():
        while True:
            gs_string = await sub_sock.recv_string()
            window.game_state.from_json(gs_string)
            ps = window.game_state.player_states[0]
            t = time.time()
            window.position_buffer.append(
                (Vec2d(ps.x, ps.y), t)
            )
            window.t = 0
            window.player_position_snapshot = copy.copy(window.player.position)

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
