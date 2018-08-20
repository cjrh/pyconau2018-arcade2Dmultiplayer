import arcade
from pymunk.vec2d import Vec2d
from demos.movement import KeysPressed, apply_movement, apply_movement_norm

class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, title="Getting Started")
        self.player_position = Vec2d(100, 100)
        self.player2 = Vec2d(100, 100)
        self.keys_pressed = KeysPressed()
        arcade.set_background_color(arcade.color.SMOKY_BLACK)

    def update(self, dt):
        self.player_position = apply_movement(
            speed=200, dt=dt, current_position=self.player_position, kp=self.keys_pressed)
        self.player2 = apply_movement_norm(
            speed=200, dt=dt, current_position=self.player2, kp=self.keys_pressed)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_rectangle_outline(
            center_x=self.player_position.x, center_y=self.player_position.y,
            width=50, height=50, color=arcade.color.SPIRO_DISCO_BALL,
            border_width=4
        )
        arcade.draw_rectangle_outline(
            center_x=self.player2.x, center_y=self.player2.y,
            width=50, height=50, color=arcade.color.YELLOW,
            border_width=4
        )

    def on_key_press(self, key, modifiers):
        self.keys_pressed.keys[key] = True

    def on_key_release(self, key, modifiers):
        self.keys_pressed.keys[key] = False

if __name__ == "__main__":
    window = MyGame(800, 600)
    arcade.run()
