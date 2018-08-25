import copy
import logging
import asyncio
import threading
import time
from collections import deque
from dataclasses import asdict
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
    def __init__(self, x, y, color, filled=True):
        self.position = Vec2d(x, y)
        self.color = color
        self.filled = filled

    def draw(self):
      if self.filled:
        arcade.draw_rectangle_filled(self.position.x, self.position.y, 50, 50, self.color)
      else:
        arcade.draw_rectangle_outline(self.position.x, self.position.y, 50, 50, self.color, border_width=4)

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, title="Multiplayer Demo")
        arcade.set_background_color(arcade.color.GRAY)
        self.game_state = GameState(player_states=[PlayerState()])
        self.player = Rectangle(0, 0, arcade.color.GREEN_YELLOW, filled=False)
        self.player_input = PlayerEvent()

    def update(self, dt):
        pass

    def on_draw(self):
        arcade.start_render()
        self.player.draw()

    def on_key_press(self, key, modifiers):
        self.player_input.keys[key] = True

    def on_key_release(self, key, modifiers):
        self.player_input.keys[key] = False


async def iomain(window: MyGame, loop):
    ctx = Context()

    sub_sock: Socket = ctx.socket(zmq.SUB)
    sub_sock.connect('tcp://localhost:25000')
    sub_sock.subscribe('')  # Required for PUB+SUB

    push_sock: Socket = ctx.socket(zmq.PUSH)
    push_sock.connect('tcp://localhost:25001')

    async def send_player_input():
        """ Task A """
        while True:
            d = asdict(window.player_input)
            msg = dict(event=d)
            await push_sock.send_json(msg)
            await asyncio.sleep(1 / UPDATE_TICK)

    async def receive_game_state():
        """ Task B """
        while True:
            gs_string = await sub_sock.recv_string()
            window.game_state.from_json(gs_string)
            ps = window.game_state.player_states[0]
            window.player.position = Vec2d(ps.x, ps.y)

    try:
        await asyncio.gather(send_player_input(), receive_game_state())
    finally:
        sub_sock.close(1)
        push_sock.close(1)
        ctx.destroy(linger=1)

def thread_worker(window: MyGame):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(iomain(window, loop))
    loop.run_forever()

def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    thread = threading.Thread(
        target=thread_worker, args=(window,), daemon=True)
    thread.start()
    arcade.run()

if __name__ == "__main__":
    main()
