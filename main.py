import turtle
import time
import random
import math

screen = turtle.Screen()
screen.setup(800, 800)
screen.bgcolor("black")
screen.tracer(0)

TILE_SIZE = 64

ITEM_SHAPE = "images/tiles/objects/Other/15.png"
INVENTORY_SHAPE = "images/gui/interface/inventory.png"

screen.addshape(ITEM_SHAPE)
screen.addshape(INVENTORY_SHAPE)

# Load animated door shapes
for direction in ["D", "U", "S", "A"]:
    for i in range(6):
        screen.addshape(f"images/tiles/animated/BigDoor_{direction}_{i}.png")

# Wall & Floor Tile Sets
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

# Register static map shapes
loaded = set()
for tile in set(LEFT_RIGHT_WALLS + UP_DOWN_WALLS + FLOOR_TILES):
    path = tile_path(tile)
    if path not in loaded:
        screen.addshape(path)
        loaded.add(path)

# Register player character shapes
for state in ["D_Walk", "U_Walk", "S_Walk", "A_Walk"]:
    for i in range(4):
        screen.addshape(f"images/players/1/{state}_{i}.png")

for state in ["U_Idle", "D_Idle", "S_Idle", "A_Idle"]:
    for i in range(4):
        screen.addshape(f"images/players/1/{state}_{i}.png")

for d in ["D", "S", "U", "A"]:
    for i in range(4):
        screen.addshape(f"images/tiles/animated/Chest2_{d}_{i}.png")

wall_rects = []
tile_sprites = []
door_sprites = []
chest_sprites = []
flying_items = []

# --- PIXEL-PERFECT INVENTORY MAPPING ---
INV_Y = -320
SLOT_OFFSETS = [-63, -21, 21, 63]

inventory_slots = [None, None, None, None]
inventory_sprites = [None, None, None, None]
selected_slot = 0

inv_ui = None
selector = None

# --- PIXEL DIALOGUE TEXT SYSTEM ---
text_painter = turtle.Turtle()
text_painter.hideturtle()
text_painter.penup()
text_painter.speed(0)

dialogue_text = ""
dialogue_timer = 0
current_prompt_type = None

def show_message(text, duration=180, prompt_type=None):
    global dialogue_text, dialogue_timer, current_prompt_type
    dialogue_text = text
    dialogue_timer = duration
    current_prompt_type = prompt_type

def draw_dialogue_box():
    if dialogue_timer <= 0 or not dialogue_text:
        text_painter.clear()
        return

    text_painter.clear()
    bx, by = 0, -220
    bw, bh = 540, 80

    # Outer Border
    text_painter.goto(bx - bw/2, by + bh/2)
    text_painter.color("#4A4A4A")
    text_painter.begin_fill()
    for _ in range(2):
        text_painter.forward(bw)
        text_painter.right(90)
        text_painter.forward(bh)
        text_painter.right(90)
    text_painter.end_fill()

    # Inner Content Box
    pad = 6
    text_painter.goto(bx - bw/2 + pad, by + bh/2 - pad)
    text_painter.color("#D3D3D3")
    text_painter.begin_fill()
    for _ in range(2):
        text_painter.forward(bw - (pad * 2))
        text_painter.right(90)
        text_painter.forward(bh - (pad * 2))
        text_painter.right(90)
    text_painter.end_fill()

    # Write message text
    text_painter.goto(bx, by - 12)
    text_painter.color("black")
    text_painter.write(dialogue_text, align="center", font=("TinyFontCraftpixPixel", 14, "normal"))

def draw_inventory_ui():
    global inv_ui, selector
    if inv_ui is not None:
        inv_ui.hideturtle()
    if selector is not None:
        selector.clear()
        selector.hideturtle()

    inv_ui = turtle.Turtle()
    inv_ui.penup()
    inv_ui.speed(0)
    inv_ui.goto(0, INV_Y)
    inv_ui.shape(INVENTORY_SHAPE)

    selector = turtle.Turtle()
    selector.hideturtle()
    selector.penup()
    selector.speed(0)
    selector.pensize(3)
    selector.color("black")
    update_selector_position()

    for idx in range(4):
        if inventory_sprites[idx] is not None:
            inventory_sprites[idx].hideturtle()
            new_item = turtle.Turtle()
            new_item.penup()
            new_item.speed(0)
            new_item.shape(inventory_slots[idx])
            new_item.goto(SLOT_OFFSETS[idx], INV_Y)
            inventory_sprites[idx] = new_item

def remove_item_from_selected_slot():
    global inventory_slots, inventory_sprites
    if inventory_sprites[selected_slot] is not None:
        inventory_sprites[selected_slot].hideturtle()
        inventory_sprites[selected_slot] = None
    inventory_slots[selected_slot] = None

def update_selector_position():
    if selector is not None:
        selector.clear()
        cx = SLOT_OFFSETS[selected_slot]
        cy = INV_Y
        half_w, half_h = 21, 21
        selector.penup()
        selector.goto(cx - half_w, cy + half_h)
        selector.pendown()
        for _ in range(2):
            selector.forward(half_w * 2)
            selector.right(90)
            selector.forward(half_h * 2)
            selector.right(90)
        selector.penup()

def select_slot(index):
    global selected_slot
    selected_slot = index
    update_selector_position()

def create_tile_sprite(x, y, tile_num):
    t = turtle.Turtle()
    t.penup()
    t.speed(0)
    t.shape(tile_path(tile_num))
    t.goto(x, y)
    tile_sprites.append(t)

def generate_room(width, height, doors_config, room_idx=0):
    for t in tile_sprites:
        t.hideturtle()
    tile_sprites.clear()
    wall_rects.clear()

    start_x = -(width * TILE_SIZE) / 2 + TILE_SIZE / 2
    start_y = (height * TILE_SIZE) / 2 - TILE_SIZE / 2

    wall_cells = set()
    for col in range(width):
        wall_cells.add((col, 0))
        wall_cells.add((col, height - 1))
    for row in range(height):
        wall_cells.add((0, row))
        wall_cells.add((width - 1, row))

    # Clear pathways out for standard structural doors
    for d in doors_config:
        gy = round((start_y - d["y"]) / TILE_SIZE)
        if d["dir"] in ["U", "D"]:
            wall_cells.discard((5, gy))
            wall_cells.discard((6, gy))

    # --- MAZE STRUCTURE DESIGN (ROOM 3) ---
    if room_idx == 3:
        # Custom maze layout segmenting coordinates
        maze_walls = [
            (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 8),
            (3, 6), (4, 2), (4, 3), (4, 4), (4, 6), (4, 8),
            (5, 4), (6, 4), (6, 7), (6, 8),
            (7, 2), (7, 3), (7, 4), (7, 6), (8, 6), (9, 2),
            (9, 3), (9, 4), (9, 5), (9, 6), (9, 7), (9, 8)
        ]
        for cell in maze_walls:
            # Constrain to ensure maze elements stay completely above the player's entrance zone
            if cell[1] < 10:
                wall_cells.add(cell)

    for row in range(height):
        for col in range(width):
            x = start_x + col * TILE_SIZE
            y = start_y - row * TILE_SIZE

            if (col, row) in wall_cells:
                tile = random.choice(LEFT_RIGHT_WALLS) if col == 0 or col == width - 1 else random.choice(UP_DOWN_WALLS)
                create_tile_sprite(x, y, tile)
                wall_rects.append((x - TILE_SIZE / 2, x + TILE_SIZE / 2, y - TILE_SIZE / 2, y + TILE_SIZE / 2))
            else:
                create_tile_sprite(x, y, random.choice(FLOOR_TILES))

def collides(x, y):
    size = 24
    left, right, bottom, top = x - size, x + size, y - size, y + size

    for wx1, wx2, wy1, wy2 in wall_rects:
        if right > wx1 and left < wx2 and top > wy1 and bottom < wy2:
            return True

    for d in doors:
        if d.frame < 5:
            dx1, dx2 = d.x - 32, d.x + 32
            dy1, dy2 = d.y - 32, d.y + 32
            if right > dx1 and left < dx2 and top > dy1 and bottom < dy2:
                return True

    for c in chests:
        cx1, cx2, cy1, cy2 = c.x - 24, c.x + 24, c.y - 24, c.y + 24
        if right > cx1 and left < cx2 and top > cy1 and bottom < cy2:
            return True

    if abs(x) > (edge_x + 10) or abs(y) > (edge_y + 10):
        return True

    return False

class Door:
    def __init__(self, x, y, direction, needs_key=False, door_id=0):
        self.x = x
        self.y = y
        self.direction = direction
        self.frame = 0
        self.target = 0
        self.is_opening = False
        self.needs_key = needs_key
        self.door_id = door_id

        if rooms[current_room]["doors_unlocked_states"].get(door_id, False):
            self.is_unlocked = True
            self.needs_key = False
        else:
            self.is_unlocked = not needs_key

        self.sprite = turtle.Turtle()
        self.sprite.penup()
        self.sprite.speed(0)
        self.sprite.shape(f"images/tiles/animated/BigDoor_{direction}_0.png")
        self.sprite.goto(x, y)
        self.sprite.shapesize(1.3)
        door_sprites.append(self.sprite)

    def update(self):
        if self.frame < self.target:
            self.frame += 1
        elif self.frame > self.target:
            self.frame -= 1

        self.sprite.shape(f"images/tiles/animated/BigDoor_{self.direction}_{self.frame}.png")

    def open_door(self):
        self.target = 5
        self.is_opening = True
        self.is_unlocked = True
        rooms[current_room]["doors_unlocked_states"][self.door_id] = True

class Chest:
    def __init__(self, x, y, direction="D", contains_key=True):
        self.x = x
        self.y = y
        self.dir = direction
        self.frame = 0
        self.state = "CLOSED"
        self.open_timer = 0
        self.has_spawned_item = False
        self.contains_key = contains_key

        self.sprite = turtle.Turtle()
        self.sprite.penup()
        self.sprite.speed(0)
        self.sprite.goto(x, y)
        self.sprite.shape(f"images/tiles/animated/Chest2_{direction}_0.png")
        chest_sprites.append(self.sprite)

    def update(self):
        if self.state == "OPENING":
            if self.frame < 3:
                self.frame += 1
            else:
                self.state = "OPEN"
                self.open_timer = 60
                self.spawn_item()
        elif self.state == "OPEN":
            if self.open_timer > 0:
                self.open_timer -= 1
            else:
                self.state = "CLOSING"
        elif self.state == "CLOSING":
            if self.frame > 0:
                self.frame -= 1
            else:
                self.state = "CLOSED"
                self.has_spawned_item = False

        self.sprite.shape(f"images/tiles/animated/Chest2_{self.dir}_{self.frame}.png")

    def open(self):
        if self.state == "CLOSED":
            self.state = "OPENING"

    def spawn_item(self):
        if not self.has_spawned_item:
            self.has_spawned_item = True

            item_id = ITEM_SHAPE if self.contains_key else "square"

            item = turtle.Turtle()
            item.penup()
            item.speed(0)
            if item_id == ITEM_SHAPE:
                item.shape(ITEM_SHAPE)
            else:
                item.shape("square")
                item.shapesize(0.5)
                item.color("gray")

            item.goto(self.x, self.y)

            flying_items.append({
                "turtle": item,
                "stage": "DRIFT",
                "target_y": self.y + 45,
                "item_id": item_id,
                "is_real_key": self.contains_key
            })

def update_items_physics():
    for i in range(len(flying_items) - 1, -1, -1):
        data = flying_items[i]
        t_obj = data["turtle"]

        if data["stage"] == "DRIFT":
            if t_obj.ycor() < data["target_y"]:
                t_obj.goto(t_obj.xcor(), t_obj.ycor() + 2)
            else:
                if data["is_real_key"]:
                    slot_idx = -1
                    for s in range(4):
                        if inventory_slots[s] is None:
                            slot_idx = s
                            break

                    if slot_idx != -1:
                        data["stage"] = "FLY_TO_INV"
                        data["dest_x"] = SLOT_OFFSETS[slot_idx]
                        data["dest_y"] = INV_Y
                        data["assigned_slot"] = slot_idx
                        inventory_slots[slot_idx] = data["item_id"]
                    else:
                        data["stage"] = "IDLE"
                else:
                    t_obj.hideturtle()
                    flying_items.pop(i)
                    show_message("Just dust inside... Keep looking!", duration=90)

        elif data["stage"] == "FLY_TO_INV":
            dx = data["dest_x"] - t_obj.xcor()
            dy = data["dest_y"] - t_obj.ycor()
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 15:
                t_obj.goto(t_obj.xcor() + (dx / distance) * 15, t_obj.ycor() + (dy / distance) * 15)
            else:
                idx = data["assigned_slot"]
                t_obj.goto(data["dest_x"], data["dest_y"])
                inventory_sprites[idx] = t_obj
                flying_items.pop(i)
                show_message("Found a key! Check if it fits the lock.", duration=120)

ROOM_WIDTH = 12
ROOM_HEIGHT = 12
edge_x = ROOM_WIDTH * TILE_SIZE / 2 - TILE_SIZE / 2
edge_y = ROOM_HEIGHT * TILE_SIZE / 2 - TILE_SIZE / 2

MAX_ROOMS = 4
current_room = 0
rooms = {}

def build_room_layout(i):
    doors_data = []
    # Every room has an upper door, including Room 3 which serves as the final exit door
    if i < MAX_ROOMS:
        needs_key = (i == 1 or i == 2)
        doors_data.append({"x": 0, "y": edge_y, "dir": "U", "needs_key": needs_key, "door_id": 100 + i})
    if i > 0:
        doors_data.append({"x": 0, "y": -edge_y, "dir": "D", "needs_key": False, "door_id": 200 + i})
    return doors_data

# Hide key inside one of the 12 chests in Room 2 (0 to 11 index)
room2_lucky_chest_idx = random.randint(0, 11)

for i in range(MAX_ROOMS):
    chests_cfg = []
    if i == 1:
        chests_cfg = [{"x": 0, "y": 0, "dir": "D", "key": True}]
    elif i == 2:
        # ROOM 2: 12 Chests (6 on each side)
        y_positions = [160, 96, 32, -32, -96, -160]
        chest_counter = 0

        # Left side chests (X = -180)
        for y_pos in y_positions:
            is_lucky = (chest_counter == room2_lucky_chest_idx)
            chests_cfg.append({"x": -180, "y": y_pos, "dir": "D", "key": is_lucky})
            chest_counter += 1

        # Right side chests (X = 180)
        for y_pos in y_positions:
            is_lucky = (chest_counter == room2_lucky_chest_idx)
            chests_cfg.append({"x": 180, "y": y_pos, "dir": "D", "key": is_lucky})
            chest_counter += 1

    rooms[i] = {
        "doors_config": build_room_layout(i),
        "doors_instances": [],
        "chests_config": chests_cfg,
        "chests_instances": [],
        "doors_unlocked_states": {}
    }

doors = []
chests = []
player = None

def load_room(i, spawn_x=0, spawn_y=None):
    global doors, chests, player, current_prompt_type
    old_dir = "D" if player is None else direction
    old_frame = 0 if player is None else frame
    current_prompt_type = None

    if spawn_y is None:
        spawn_y = -edge_y + 90

    for sprite in door_sprites:
        sprite.hideturtle()
    door_sprites.clear()

    for sprite in chest_sprites:
        sprite.hideturtle()
    chest_sprites.clear()
    chests.clear()

    for item_data in flying_items:
        item_data["turtle"].hideturtle()
    flying_items.clear()

    if player is not None:
        player.hideturtle()

    generate_room(ROOM_WIDTH, ROOM_HEIGHT, rooms[i]["doors_config"], room_idx=i)

    rooms[i]["doors_instances"] = [
        Door(d["x"], d["y"], d["dir"], d["needs_key"], d["door_id"]) for d in rooms[i]["doors_config"]
    ]
    doors = rooms[i]["doors_instances"]

    rooms[i]["chests_instances"] = [
        Chest(c["x"], c["y"], c["dir"], c["key"]) for c in rooms[i]["chests_config"]
    ]
    chests = rooms[i]["chests_instances"]

    player = turtle.Turtle()
    player.penup()
    player.speed(0)
    player.goto(spawn_x, spawn_y)
    player.shape(f"images/players/1/{old_dir}_Idle_{old_frame}.png")

    draw_inventory_ui()

    if i == 0:
        show_message("Welcome! Head through the door to find the chest room.", duration=180)
    elif i == 1:
        show_message("Open the central chest to obtain the maze key card!", duration=180)
    elif i == 2:
        show_message("Find the real key hidden within the 12 side chests!", duration=200)
    elif i == 3:
        show_message("Maze Room reached! Traverse up to the escape door.", duration=240)

# --- STATE CONTROLLER FOR START & END SCREEN ---
game_state = "START_SCREEN"
ui_painter = turtle.Turtle()
ui_painter.hideturtle()
ui_painter.penup()
ui_painter.color("white")

def draw_cool_start_scene():
    for y_idx in range(-3, 4):
        for x_idx in range(-3, 4):
            create_tile_sprite(x_idx * TILE_SIZE, y_idx * TILE_SIZE, random.choice(FLOOR_TILES))

    ui_painter.goto(0, 180)
    ui_painter.write("THE LOST DUNGEON", align="center", font=("TinyFontCraftpixPixel", 36, "bold"))
    ui_painter.goto(0, -180)
    ui_painter.write("PRESS ENTER TO START", align="center", font=("TinyFontCraftpixPixel", 16, "normal"))

def draw_victory_screen():
    global game_state
    game_state = "VICTORY"
    
    player.hideturtle()
    if inv_ui is not None: inv_ui.hideturtle()
    if selector is not None: selector.clear()
    for d in door_sprites: d.hideturtle()
    for c in chest_sprites: c.hideturtle()
    text_painter.clear()
    
    screen.bgcolor("#11111d")
    ui_painter.clear()
    ui_painter.color("#4af626")
    ui_painter.goto(0, 40)
    ui_painter.write("DUNGEON ESCAPED!", align="center", font=("TinyFontCraftpixPixel", 32, "bold"))
    ui_painter.color("white")
    ui_painter.goto(0, -30)
    ui_painter.write("You have completely escaped The Lost Dungeon!", align="center", font=("TinyFontCraftpixPixel", 16, "normal"))
    ui_painter.goto(0, -70)
    ui_painter.write("Thank you for playing!", align="center", font=("TinyFontCraftpixPixel", 14, "italic"))

def start_game():
    global game_state, player, frame, timer
    if game_state == "START_SCREEN":
        ui_painter.clear()
        for t in tile_sprites:
            t.hideturtle()
        tile_sprites.clear()

        game_state = "PLAYING"
        load_room(0, spawn_x=0, spawn_y=-edge_y + 90)

draw_cool_start_scene()

player = turtle.Turtle()
player.penup()
player.speed(0)
player.goto(0, 0)
player.shape("images/players/1/D_Idle_0.png")

speed = 5
keys = {k: False for k in "wasde"}

screen.onkeypress(start_game, "Return")
screen.onkeypress(lambda: keys.__setitem__("w", True), "w")
screen.onkeypress(lambda: keys.__setitem__("a", True), "a")
screen.onkeypress(lambda: keys.__setitem__("s", True), "s")
screen.onkeypress(lambda: keys.__setitem__("d", True), "d")
screen.onkeypress(lambda: keys.__setitem__("e", True), "e")

screen.onkeypress(lambda: select_slot(0), "1")
screen.onkeypress(lambda: select_slot(1), "2")
screen.onkeypress(lambda: select_slot(2), "3")
screen.onkeypress(lambda: select_slot(3), "4")

screen.onkeyrelease(lambda: keys.__setitem__("w", False), "w")
screen.onkeyrelease(lambda: keys.__setitem__("a", False), "a")
screen.onkeyrelease(lambda: keys.__setitem__("s", False), "s")
screen.onkeyrelease(lambda: keys.__setitem__("d", False), "d")
screen.onkeyrelease(lambda: keys.__setitem__("e", False), "e")

screen.listen()

frame = 0
timer = 0
direction = "D"
active_transition = None
transition_timer = 0

# Game Loop
while True:
    if game_state == "START_SCREEN":
        timer += 1
        if timer >= 12:
            frame = (frame + 1) % 4
            timer = 0
        player.shape(f"images/players/1/D_Idle_{frame}.png")

    elif game_state == "PLAYING":
        if active_transition is None:
            x, y = player.xcor(), player.ycor()
            nx, ny = x, y
            moving = False

            if keys["w"]:
                ny += speed
                direction = "U"
                moving = True
            if keys["s"]:
                ny -= speed
                direction = "D"
                moving = True
            if keys["a"]:
                nx -= speed
                direction = "S"
                moving = True
            if keys["d"]:
                nx += speed
                direction = "A"
                moving = True

            if not collides(nx, y): x = nx
            if not collides(x, ny): y = ny
            player.goto(x, y)

            timer += 1
            if timer >= 12:
                frame = (frame + 1) % 4
                timer = 0

            detected_prompt = None

            # Interactions & Prompts
            for d in doors:
                dist = abs(player.xcor() - d.x) + abs(player.ycor() - d.y)
                if dist < 100:
                    if d.frame < 5:
                        detected_prompt = "PROMPT_DOOR"

                    if keys["e"]:
                        if d.needs_key and not d.is_unlocked:
                            if inventory_slots[selected_slot] == ITEM_SHAPE:
                                d.open_door()
                                remove_item_from_selected_slot()
                                active_transition = d
                                transition_timer = 0
                            else:
                                show_message("This door is locked, find the key to open the door!", duration=120)
                        else:
                            d.open_door()
                            active_transition = d
                            transition_timer = 0
                        keys["e"] = False

            for c in chests:
                dist = abs(player.xcor() - c.x) + abs(player.ycor() - c.y)
                if dist < 80:
                    if c.state == "CLOSED":
                        detected_prompt = "PROMPT_CHEST"

                    if keys["e"]:
                        c.open()
                        keys["e"] = False

            # Stable Interface updates
            if detected_prompt == "PROMPT_DOOR" and current_prompt_type != "PROMPT_DOOR" and dialogue_timer <= 0:
                show_message("Press E to open the door", duration=9999, prompt_type="PROMPT_DOOR")
            elif detected_prompt == "PROMPT_CHEST" and current_prompt_type != "PROMPT_CHEST" and dialogue_timer <= 0:
                show_message("Press E to open the chest", duration=9999, prompt_type="PROMPT_CHEST")
            elif detected_prompt is None and current_prompt_type in ["PROMPT_DOOR", "PROMPT_CHEST"]:
                dialogue_text = ""
                dialogue_timer = 0
                current_prompt_type = None

        else:
            transition_timer += 1
            if transition_timer >= 24 and active_transition.frame >= 5:
                d = active_transition
                # If going through the top door of Room 3, trigger game victory completion
                if d.direction == "U" and current_room == 3:
                    draw_victory_screen()
                elif d.direction == "U" and current_room < MAX_ROOMS - 1:
                    current_room += 1
                    load_room(current_room, spawn_x=0, spawn_y=-edge_y + 90)
                elif d.direction == "D" and current_room > 0:
                    current_room -= 1
                    load_room(current_room, spawn_x=0, spawn_y=edge_y - 90)
                active_transition = None

        if game_state == "PLAYING":
            for c in chests:
                c.update()

            update_items_physics()

            for d in doors:
                d.update()

            player.shape(
                f"images/players/1/{direction}_Walk_{frame}.png"
                if moving and active_transition is None else
                f"images/players/1/{direction}_Idle_{frame}.png"
            )

            if dialogue_timer > 0 and current_prompt_type is None:
                dialogue_timer -= 1
            draw_dialogue_box()

    screen.update()
    time.sleep(1 / 60)