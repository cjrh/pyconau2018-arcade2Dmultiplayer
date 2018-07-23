import asyncio
import threading
from typing import Dict
import zmq
from zmq.asyncio import Context, Socket
import arcade
from pymunk.vec2d import Vec2d
from .lib02 import PlayerEvent, PlayerState, GameState


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50

MOVEMENT_SPEED = 5
UPDATE_TICK = 10

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

    def setup(self):
        x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2
        self.player.position += Vec2d(x, y)

    def update(self, dt):
        # TODO: actually nothing to do here (until interpolation)
        # self.player.move()
        pass

    def on_draw(self):
        arcade.start_render()
        # TODO: draw the full game state
        self.player.position.x = self.game_state.player_states[0].x
        self.player.position.y = self.game_state.player_states[0].y

        self.player.draw()

    def on_key_press(self, key, modifiers):
        # TODO: update the player state
        # self.player.movement[key] = MOVE_MAP[key] * MOVEMENT_SPEED
        print(key)
        self.player_event.left |= key == arcade.key.LEFT
        self.player_event.right |= key == arcade.key.RIGHT
        self.player_event.up |= key == arcade.key.UP
        self.player_event.down |= key == arcade.key.DOWN

    def on_key_release(self, key, modifiers):
        print(key)
        # TODO: update the player state
        # del self.player.movement[key]
        self.player_event.left ^= key == arcade.key.LEFT
        self.player_event.right ^= key == arcade.key.RIGHT
        self.player_event.up ^= key == arcade.key.UP
        self.player_event.down ^= key == arcade.key.DOWN

        # if arcade.key.LEFT:
        #     self.player_event.left = False
        # elif arcade.key.RIGHT:
        #     self.player_event.right = False
        # elif arcade.key.UP:
        #     self.player_event.up = False
        # elif arcade.key.DOWN:
        #     self.player_event.down = False


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
            # print(d)
            await push_sock.send_json(d)
            await asyncio.sleep(1 / UPDATE_TICK)

    async def receive_game_state():
        while True:
            gs_string = await sub_sock.recv_string()
            print('.', end='', flush=True)
            window.game_state.from_json(gs_string)

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
