import arcade
from pymunk.vec2d import Vec2d
from demos.movement import KeysPressed, MOVE_MAP, apply_movement

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, title="Getting Started")
        self.player_position = Vec2d(400, 300)
        self.keys_pressed = KeysPressed()

    def update(self, dt):
        self.player_position = apply_movement(
            speed=600, dt=dt, current_position=self.player_position, kp=self.keys_pressed)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_rectangle_filled(
            center_x=self.player_position.x, center_y=self.player_position.y,
            width=50, height=50, color=arcade.color.GREEN_YELLOW, tilt_angle=0)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.keys[key] = True

    def on_key_release(self, key, modifiers):
        self.keys_pressed.keys[key] = False

if __name__ == "__main__":
    window = MyGame(800, 600)
    arcade.run()
