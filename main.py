import turtle
import time
import random

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("black")
screen.tracer(0)

TILE_SIZE = 64

LEFT_RIGHT_WALLS = [
    3, 7, 9, 13, 19, 23, 33, 37,
    44, 48, 52, 79, 80, 81,
    87, 88, 92
]

UP_DOWN_WALLS = [
    4, 5, 6, 11, 24, 27, 28,
    49, 53, 57, 58, 59, 60, 61,
    75, 77, 86, 89, 91, 93,
    97, 98, 99, 101, 102, 105
]

FLOOR_TILES = [
    20, 21, 22, 34, 35, 36, 39,
    45, 46, 47,
    72, 73, 74, 76,
    82, 83, 84,
    94, 95, 96,
    107, 108, 109
]

def tile_path(num):
    return f"images/tiles/tiles/Tile_{num:02d}.png"

loaded = set()

for tile in set(LEFT_RIGHT_WALLS + UP_DOWN_WALLS + FLOOR_TILES):
    path = tile_path(tile)
    if path not in loaded:
        screen.addshape(path)
        loaded.add(path)

for state in ["D_Idle", "D_Walk", "U_Walk", "S_Walk", "A_Walk"]:
    for i in range(4):
        screen.addshape(f"images/players/1/{state}_{i}.png")

drawer = turtle.Turtle()
drawer.hideturtle()
drawer.penup()
drawer.speed(0)

wall_rects = []

def draw_tile(x, y, tile):
    drawer.goto(x, y)
    drawer.shape(tile_path(tile))
    drawer.stamp()

def generate_room(width=12, height=12):
    drawer.clearstamps()
    wall_rects.clear()

    start_x = -(width * TILE_SIZE) / 2 + TILE_SIZE / 2
    start_y = (height * TILE_SIZE) / 2 - TILE_SIZE / 2

    for row in range(height):
        for col in range(width):

            x = start_x + col * TILE_SIZE
            y = start_y - row * TILE_SIZE

            if (
                col == 0 or
                col == width - 1 or
                row == 0 or
                row == height - 1
            ):

                if col == 0 or col == width - 1:
                    tile = random.choice(LEFT_RIGHT_WALLS)
                else:
                    tile = random.choice(UP_DOWN_WALLS)

                wall_rects.append(
                    (
                        x - TILE_SIZE / 2,
                        x + TILE_SIZE / 2,
                        y - TILE_SIZE / 2,
                        y + TILE_SIZE / 2
                    )
                )

            else:
                tile = random.choice(FLOOR_TILES)

            draw_tile(x, y, tile)

def collides(x, y):
    size = 32

    left = x - size
    right = x + size
    bottom = y - size
    top = y + size

    for wx1, wx2, wy1, wy2 in wall_rects:
        if (
            right > wx1 and
            left < wx2 and
            top > wy1 and
            bottom < wy2
        ):
            return True

    return False

class Door:

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction

        self.frame = 0
        self.target_frame = 0

        self.sprite = turtle.Turtle()
        self.sprite.penup()
        self.sprite.shape(
            f"images/tiles/animated/BigDoor_{direction}_0.png"
        )

        self.sprite.goto(x, y)

    def update(self):

        if self.frame < self.target_frame:
            self.frame += 1

        elif self.frame > self.target_frame:
            self.frame -= 1

        self.sprite.shape(
            f"images/tiles/animated/BigDoor_{self.direction}_{self.frame}.png"
        )

    def open(self):
        self.target_frame = 5

    def close(self):
        self.target_frame = 0

    def toggle(self):
        if self.target_frame == 0:
            self.open()
        else:
            self.close()

    def set_highlight(self, highlighted):
        if highlighted:
            self.sprite.shapesize(1.15)
        else:
            self.sprite.shapesize(1.0)

ROOM_WIDTH = 12
ROOM_HEIGHT = 12

generate_room(ROOM_WIDTH, ROOM_HEIGHT)

edge_x = ROOM_WIDTH * TILE_SIZE / 2 - TILE_SIZE / 2
edge_y = ROOM_HEIGHT * TILE_SIZE / 2 - TILE_SIZE / 2

doors = [
    Door(0, edge_y, "U"),
    Door(0, -edge_y, "D"),
    Door(-edge_x, 0, "S"),
    Door(edge_x, 0, "A")
]

player = turtle.Turtle()
player.penup()
player.shape("images/players/1/D_Idle_0.png")
player.goto(0, 0)

for direction in ["D", "U", "S", "A"]:
    for i in range(6):
        screen.addshape(
            f"images/tiles/animated/BigDoor_{direction}_{i}.png"
        )

speed = 5

keys = {
    "w": False,
    "a": False,
    "s": False,
    "d": False,
    "e": False
}

screen.onkeypress(lambda: keys.__setitem__("w", True), "w")
screen.onkeypress(lambda: keys.__setitem__("a", True), "a")
screen.onkeypress(lambda: keys.__setitem__("s", True), "s")
screen.onkeypress(lambda: keys.__setitem__("d", True), "d")
screen.onkeypress(lambda: keys.__setitem__("e", True), "e")

screen.onkeyrelease(lambda: keys.__setitem__("e", False), "e")
screen.onkeyrelease(lambda: keys.__setitem__("w", False), "w")
screen.onkeyrelease(lambda: keys.__setitem__("a", False), "a")
screen.onkeyrelease(lambda: keys.__setitem__("s", False), "s")
screen.onkeyrelease(lambda: keys.__setitem__("d", False), "d")

screen.listen()

frame = 0
animation_timer = 0
direction = "D"

while True:

    x = player.xcor()
    y = player.ycor()

    new_x = x
    new_y = y

    moving = False

    if keys["w"]:
        new_y += speed
        direction = "U"
        moving = True

    if keys["s"]:
        new_y -= speed
        direction = "D"
        moving = True

    if keys["a"]:
        new_x -= speed
        direction = "S"
        moving = True

    if keys["d"]:
        new_x += speed
        direction = "A"
        moving = True

    if not collides(new_x, y):
        x = new_x

    if not collides(x, new_y):
        y = new_y

    player.goto(x, y)

    animation_timer += 1

    if animation_timer >= 12:
        frame = (frame + 1) % 4
        animation_timer = 0

    if moving:
        player.shape(f"images/players/1/{direction}_Walk_{frame}.png")
    else:
        player.shape(f"images/players/1/D_Idle_{frame}.png")

    nearest = None
    nearest_distance = 999999

    for door in doors:

        distance = (
            (player.xcor() - door.x) ** 2 +
            (player.ycor() - door.y) ** 2
        ) ** 0.5

        highlighted = distance < 80

        door.set_highlight(highlighted)

        if distance < nearest_distance:
            nearest_distance = distance
            nearest = door

        door.update()

    if keys["e"] and nearest_distance < 80:
        nearest.toggle()
        keys["e"] = False
    screen.update()
    time.sleep(1 / 60)