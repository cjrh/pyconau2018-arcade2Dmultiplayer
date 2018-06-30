from typing import Dict
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50

MOVEMENT_SPEED = 5


class Vector:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def constrain(self, xmin, xmax, ymin, ymax):
        if self.x < xmin + RECT_WIDTH // 2:
            self.x = xmin + RECT_WIDTH // 2
        if self.x > xmax - (RECT_WIDTH // 2):
            self.x = xmax - (RECT_WIDTH // 2)

        if self.y < ymin + RECT_HEIGHT // 2:
            self.y = ymin + RECT_HEIGHT // 2
        if self.y > ymax - (RECT_HEIGHT // 2):
            self.y = ymax - (RECT_HEIGHT // 2)


MOVE_MAP = {
    arcade.key.UP: Vector(0, 1),
    arcade.key.DOWN: Vector(0, -1),
    arcade.key.LEFT: Vector(-1, 0),
    arcade.key.RIGHT: Vector(1, 0),
}


class Rectangle:
    def __init__(self, x, y, width, height, angle, color):
        self.position = Vector(x, y)
        self.movement: Dict[Vector] = {}

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

    def move(self):
        for vec in self.movement.values():
            self.position += vec
        self.position.constrain(
            xmin=0, xmax=SCREEN_WIDTH,
            ymin=0, ymax=SCREEN_HEIGHT,
        )


class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height, title="Keyboard control")
        self.player = None
        self.left_down = False

    def setup(self):
        width = RECT_WIDTH
        height = RECT_HEIGHT
        x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2
        angle = 0
        color = arcade.color.WHITE
        self.player = Rectangle(x, y, width, height, angle, color)
        self.left_down = False

    def update(self, dt):
        self.player.move()

    def on_draw(self):
        arcade.start_render()
        self.player.draw()

    def on_key_press(self, key, modifiers):
        self.player.movement[key] = MOVE_MAP[key] * MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        del self.player.movement[key]


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
