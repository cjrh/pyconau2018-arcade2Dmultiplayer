import arcade
from pymunk import Vec2d

MOVE_MAP = {
    arcade.key.UP: Vec2d(0, 1),
    arcade.key.DOWN: Vec2d(0, -1),
    arcade.key.LEFT: Vec2d(-1, 0),
    arcade.key.RIGHT: Vec2d(1, 0),
}

class KeysPressed:
    def __init__(self):
        self.keys = {k: False for k in MOVE_MAP}

def apply_movement(speed, dt, current_position: Vec2d, kp: KeysPressed) -> Vec2d:
    delta_position = sum(kp.keys[k] * MOVE_MAP[k] for k in kp.keys)
    return current_position + delta_position * speed * dt

def apply_movement_norm(speed, dt, current_position: Vec2d, kp: KeysPressed) -> Vec2d:
    delta_position = sum(kp.keys[k] * MOVE_MAP[k] for k in kp.keys)
    return current_position + delta_position.normalized() * speed * dt
