import copy

import arcade
from pymunk import Vec2d


KEYS = [arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT]


class KeysPressed:
    def __init__(self):
        self.keys = {k: False for k in KEYS}


MOVE_MAP = {
    arcade.key.UP: Vec2d(0, 1),
    arcade.key.DOWN: Vec2d(0, -1),
    arcade.key.LEFT: Vec2d(-1, 0),
    arcade.key.RIGHT: Vec2d(1, 0),
}


def apply_movement(speed, dt, current_position: Vec2d, kp: KeysPressed) -> Vec2d:
    p = copy.copy(current_position)
    for k in kp.keys:
        p += kp.keys[k] * MOVE_MAP[k] * speed * dt
    return p
