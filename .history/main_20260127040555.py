import pygame
from cave import generate_cave
from cave import rearrange_gates
from map import draw_map

# ======================
# CONFIGURATION
# ======================

LEVELS = ["easy", "medium", "hard"]
current_level_index = 0
LEVEL = LEVELS[current_level_index]

def set_level_from_index():
    global LEVEL, WORLD_ROWS, WORLD_COLS, MAP_NUM, FOOD_NUM, LIGHT_NUM, GATE_NUM, ENEMY_COUNT
    LEVEL = LEVELS[current_level_index]
    if LEVEL == "easy":
        WORLD_ROWS = 46
        WORLD_COLS = 50
        MAP_NUM = 30
        FOOD_NUM = 8
        LIGHT_NUM = 8
        GATE_NUM = 10
        ENEMY_COUNT = 10
    elif LEVEL == "medium":
        WORLD_ROWS = 71
        WORLD_COLS = 75
        MAP_NUM = 6
        FOOD_NUM = 16
        LIGHT_NUM = 16
        GATE_NUM = 20
        ENEMY_COUNT = 20
    elif LEVEL == "hard":
        WORLD_ROWS = 96
        WORLD_COLS = 100
        MAP_NUM = 12
        FOOD_NUM = 32
        LIGHT_NUM = 32
        GATE_NUM = 40
        ENEMY_COUNT = 40

set_level_from_index()

DENSITY = 0.2
MAX_ROOM_SIZE = 10
MIN_ROOM_SIZE = 3

VIEW_ROWS = 7
VIEW_COLS = 11

BASE_CELL_SIZE = 128
WALL_SCALE = 1

FPS = 60

BLACK = (0, 0, 0)
LIGHT_GRAY = (98, 87, 85)
GREEN = (0, 200, 0)

inventory = {
    "FOOD": 0,
    "MAP": 0
}

trade_options = {
    "FOOD_ENERGY": "Food -> Energy",
    "FOOD_LIGHT": "Food -> Light +50%",
    "FOOD_MAP": "Food -> Map +1",
    "MAP_ENERGY": "Map -> Energy +50%",
    "MAP_LIGHT": "Map -> Light +50%",
    "BACK": "Back"
}



# ======================
# MOVEMENT
# ======================

MAX_MOVE_SPEED = 500
MIN_MOVE_SPEED = 0

# ======================
# LIGHT
# ======================

MAX_LIGHT = 100
MIN_LIGHT = 10
LIGHT_DRAIN_PER_SEC = 0.85

# ======================
# ENERGY
# ======================

MAX_ENERGY = 100
MIN_ENERGY = 0
ENERGY_DRAIN_PER_SEC = 0.6

# ======================
# ENEMIES
# ======================
ENEMY_SPEED = 100  # pixels per second
ENEMY_TRIGGER_LIGHT = 20  # light % at which enemies start moving

# ======================
# TILE CONSTANTS
# ======================

WALL = 1
FLOOR = 0
EXIT = 2
MAP = 3
FOOD = 4
LIGHT = 5
GATE_CLOSED = 6
GATE_OPEN = 7

# ======================
# INIT
# ======================

pygame.init()
SCREEN_WIDTH = VIEW_COLS * BASE_CELL_SIZE
SCREEN_HEIGHT = VIEW_ROWS * BASE_CELL_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cave Explorer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

wall_image = pygame.image.load("assets/wall_block.jpg")
wall_image = pygame.transform.scale(
    wall_image, (BASE_CELL_SIZE, BASE_CELL_SIZE)
)

# ======================
# SPRITES
# ======================

character_sheet = pygame.image.load("assets/chars.jpg")

SPRITE_WIDTH = 177.5
SPRITE_HEIGHT = 205.5
FRAMES = 4

def extract_frames(row):
    frames = []
    for col in range(FRAMES):
        frame = character_sheet.subsurface(
            pygame.Rect(
                col * SPRITE_WIDTH,
                row * SPRITE_HEIGHT,
                SPRITE_WIDTH,
                SPRITE_HEIGHT,
            )
        )
        frames.append(
            pygame.transform.scale(
                frame, (BASE_CELL_SIZE // 2, BASE_CELL_SIZE // 2)
            )
        )
    return frames

sprites = {
    "down": extract_frames(0),
    "left": extract_frames(1),
    "right": extract_frames(2),
    "up": extract_frames(3),
}

# ======================
# ITEM IMAGES
# ======================

map_image = pygame.image.load("assets/map.jpg")
map_image = pygame.transform.scale(map_image, (BASE_CELL_SIZE // 2, BASE_CELL_SIZE // 2))

food_image = pygame.image.load("assets/food.jpg")
food_image = pygame.transform.scale(food_image, (BASE_CELL_SIZE // 2, BASE_CELL_SIZE // 2))

light_image = pygame.image.load("assets/light.jpg")
light_image = pygame.transform.scale(light_image, (BASE_CELL_SIZE // 2, BASE_CELL_SIZE // 2))

# Gates
gate_closed_h = pygame.image.load("assets/doors/closed_horizontal.jpg")
gate_closed_h = pygame.transform.scale(gate_closed_h, (BASE_CELL_SIZE, BASE_CELL_SIZE))
gate_closed_v = pygame.image.load("assets/doors/closed_vertical.jpg")
gate_closed_v = pygame.transform.scale(gate_closed_v, (BASE_CELL_SIZE, BASE_CELL_SIZE))

gate_open_h = pygame.image.load("assets/doors/open_horizontal.jpg")
gate_open_h = pygame.transform.scale(gate_open_h, (BASE_CELL_SIZE, BASE_CELL_SIZE))
gate_open_v = pygame.image.load("assets/doors/open_vertical.jpg")
gate_open_v = pygame.transform.scale(gate_open_v, (BASE_CELL_SIZE, BASE_CELL_SIZE))

finish_image = pygame.image.load("assets/finish.jpg")
finish_image = pygame.transform.scale(finish_image, (BASE_CELL_SIZE, BASE_CELL_SIZE))

# Monsters
MONSTER_SIZE = BASE_CELL_SIZE // 2
monster_left = pygame.image.load("assets/monleft.jpg")
monster_left = pygame.transform.scale(monster_left, (MONSTER_SIZE, MONSTER_SIZE))
monster_right = pygame.image.load("assets/monright.jpg")
monster_right = pygame.transform.scale(monster_right, (MONSTER_SIZE, MONSTER_SIZE))

# ======================
# GAME STATE
# ======================

GAME_STATE = "MENU"  # MENU, PLAYING, HOWTO

cave = None
player_x = player_y = 0
player_radius = BASE_CELL_SIZE // 4

player_direction = "down"
animation_frame = 0
animation_timer = 0
ANIM_SPEED = 0.15

light_percentage = MAX_LIGHT
energy_percentage = MAX_ENERGY
map_count = 0  # Number of times player can open the map after collecting MAP

show_map = False

# ======================
# HELPERS
# ======================

def can_move_pixel(x, y):
    for ox in (-player_radius, player_radius):
        for oy in (-player_radius, player_radius):
            cx = int((x + ox) // BASE_CELL_SIZE)
            cy = int((y + oy) // BASE_CELL_SIZE)
            if not (0 <= cx < WORLD_COLS and 0 <= cy < WORLD_ROWS):
                return False
            if cave[cy][cx] in (WALL, GATE_CLOSED):
                return False
    return True

def get_camera_offset():
    cam_x = player_x - SCREEN_WIDTH // 2
    cam_y = player_y - SCREEN_HEIGHT // 2
    cam_x = max(0, min(cam_x, WORLD_COLS * BASE_CELL_SIZE - SCREEN_WIDTH))
    cam_y = max(0, min(cam_y, WORLD_ROWS * BASE_CELL_SIZE - SCREEN_HEIGHT))
    return int(cam_x), int(cam_y)

# ======================
# UI ELEMENTS
# ======================

def draw_map_button():
    rect = pygame.Rect(SCREEN_WIDTH - 110, 10, 100, 40)
    pygame.draw.rect(screen, (80, 80, 80), rect)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)
    text = font.render("MAP (M)", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=rect.center))
    return rect

def draw_trade_button():
    rect = pygame.Rect(SCREEN_WIDTH - 110, 60, 100, 40)
    pygame.draw.rect(screen, (80, 80, 80), rect)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)
    text = font.render("TRADE", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=rect.center))
    return rect


def draw_bar(x, y, value, label, color):
    w, h = 200, 20
    pygame.draw.rect(screen, (50, 50, 50), (x, y, w, h))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h), 2)
    pygame.draw.rect(screen, color, (x, y, int(w * value / 100), h))
    txt = font.render(f"{label}: {int(value)}%", True, (255, 255, 255))
    screen.blit(txt, (x + w + 10, y + 3))

def draw_back_button():
    rect = pygame.Rect(10, 10, 120, 40)
    pygame.draw.rect(screen, (80, 80, 80), rect)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)
    text = font.render("BACK", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=rect.center))
    return rect

# ======================
# LIGHT OVERLAY
# ======================

def draw_light_overlay():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))
    radius = int((SCREEN_HEIGHT // 2) * (light_percentage / 100))
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    for r in range(radius, 0, -1):
        alpha = int(230 * (r / radius) ** 2)
        pygame.draw.circle(overlay, (0, 0, 0, alpha), center, r)

    screen.blit(overlay, (0, 0))

# ======================
# WORLD RENDER
# ======================

def draw_world():
    cam_x, cam_y = get_camera_offset()

    for r in range(VIEW_ROWS):
        for c in range(VIEW_COLS):
            wx = c + cam_x // BASE_CELL_SIZE
            wy = r + cam_y // BASE_CELL_SIZE
            sx = c * BASE_CELL_SIZE - cam_x % BASE_CELL_SIZE
            sy = r * BASE_CELL_SIZE - cam_y % BASE_CELL_SIZE

            if not (0 <= wx < WORLD_COLS and 0 <= wy < WORLD_ROWS):
                continue

            tile = cave[wy][wx]

            # Draw walls and gates
            if tile == WALL:
                screen.blit(wall_image, (sx, sy))
            elif tile in (GATE_CLOSED, GATE_OPEN):
                # Decide orientation from surrounding walls
                left_wall = (wx > 0 and cave[wy][wx-1] == WALL)
                right_wall = (wx < WORLD_COLS-1 and cave[wy][wx+1] == WALL)
                up_wall = (wy > 0 and cave[wy-1][wx] == WALL)
                down_wall = (wy < WORLD_ROWS-1 and cave[wy+1][wx] == WALL)

                horizontal = up_wall and down_wall   # corridor is horizontal
                vertical = left_wall and right_wall   # corridor is vertical

                if tile == GATE_CLOSED:
                    sprite = gate_closed_h if horizontal else gate_closed_v
                else:
                    sprite = gate_open_h if horizontal else gate_open_v
                screen.blit(sprite, (sx, sy))
            elif tile==EXIT:
                screen.blit(finish_image, (sx, sy))
            else:
                pygame.draw.rect(screen, LIGHT_GRAY,
                                 (sx, sy, BASE_CELL_SIZE, BASE_CELL_SIZE))

            # Draw items as small circles on floor
            circle_radius = BASE_CELL_SIZE // 4
            circle_center = (sx + BASE_CELL_SIZE // 2, sy + BASE_CELL_SIZE // 2)

            if tile in (MAP, FOOD, LIGHT):
                if tile == MAP:
                    item_rect = map_image.get_rect(center=circle_center)
                    screen.blit(map_image, item_rect)
                elif tile == FOOD:
                    item_rect = food_image.get_rect(center=circle_center)
                    screen.blit(food_image, item_rect)
                elif tile == LIGHT:
                    item_rect = light_image.get_rect(center=circle_center)
                    screen.blit(light_image, item_rect)

    # Draw player sprite
    sprite = sprites[player_direction][animation_frame]
    screen.blit(sprite, sprite.get_rect(center=(player_x - cam_x, player_y - cam_y)))
    # Draw enemies
    for enemy in enemies:
        sprite = monster_right if enemy.get("dir") == "right" else monster_left
        rect = sprite.get_rect(center=(int(enemy["x"] - cam_x), int(enemy["y"] - cam_y)))
        screen.blit(sprite, rect)


# ======================
# MENU
# ======================

def draw_menu(mouse):
    screen.fill((20, 20, 20))
    title = pygame.font.SysFont(None, 64).render(
        "CAVE EXPLORER", True, (240, 240, 240)
    )
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))

    buttons = {}
    w, h = 260, 60
    y = 220

    labels = ["NEW GAME", "LEVEL", "HOW TO PLAY", "QUIT"]
    for i, label in enumerate(labels):
        rect = pygame.Rect(SCREEN_WIDTH//2-w//2, y+i*80, w, h)
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (120,120,120) if hover else (80,80,80), rect)
        pygame.draw.rect(screen, (200,200,200), rect, 2)

        # For LEVEL, show current level
        if label == "LEVEL":
            text_label = f"LEVEL: {LEVEL.upper()}"
        else:
            text_label = label

        screen.blit(font.render(text_label, True, (255,255,255)),
                    font.render(text_label, True, (255,255,255)).get_rect(center=rect.center))
        buttons[label] = rect
    return buttons

def draw_inventory():
    x, y = 10, SCREEN_HEIGHT - 100
    txt = font.render(f"Inventory: FOOD={inventory['FOOD']} MAP={inventory['MAP']}", True, (255, 255, 255))
    screen.blit(txt, (x, y))


def draw_win_screen():
    screen.fill((20, 20, 20))  # Same tone as MENU background

    title_font = pygame.font.SysFont(None, 64)
    msg_font = pygame.font.SysFont(None, 28)

    title = title_font.render("YOU ESCAPED!", True, (200, 255, 200))
    subtitle = msg_font.render(
        "Congratulations, you found the exit.",
        True,
        (220, 220, 220),
    )

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 160)))
    screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 210)))

    # ---------- BUTTONS ----------
    btn_w, btn_h = 260, 60
    spacing = 80
    mouse = pygame.mouse.get_pos()

    # NEW GAME button
    new_game_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        300,
        btn_w,
        btn_h,
    )
    hover = new_game_rect.collidepoint(mouse)
    pygame.draw.rect(
        screen,
        (120, 120, 120) if hover else (80, 80, 80),
        new_game_rect,
    )
    pygame.draw.rect(screen, (200, 200, 200), new_game_rect, 2)

    new_game_text = msg_font.render("NEW GAME", True, (255, 255, 255))
    screen.blit(
        new_game_text,
        new_game_text.get_rect(center=new_game_rect.center),
    )

    # BACK TO MENU button
    menu_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        300 + spacing,
        btn_w,
        btn_h,
    )
    hover = menu_rect.collidepoint(mouse)
    pygame.draw.rect(
        screen,
        (120, 120, 120) if hover else (80, 80, 80),
        menu_rect,
    )
    pygame.draw.rect(screen, (200, 200, 200), menu_rect, 2)

    menu_text = msg_font.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(
        menu_text,
        menu_text.get_rect(center=menu_rect.center),
    )

    return new_game_rect, menu_rect



def draw_game_over_screen():
    screen.fill((20, 20, 20))  # Same background as MENU

    title_font = pygame.font.SysFont(None, 64)
    msg_font = pygame.font.SysFont(None, 28)

    title = title_font.render("GAME OVER", True, (255, 120, 120))
    subtitle = msg_font.render("You ran out of energy.", True, (220, 220, 220))

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))
    screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200)))

    # ---------- BUTTONS ----------
    btn_w, btn_h = 260, 60
    spacing = 80
    mouse = pygame.mouse.get_pos()

    # New Game button
    new_game_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        280,
        btn_w,
        btn_h,
    )
    hover = new_game_rect.collidepoint(mouse)
    pygame.draw.rect(screen, (120,120,120) if hover else (80,80,80), new_game_rect)
    pygame.draw.rect(screen, (200,200,200), new_game_rect, 2)

    new_game_text = msg_font.render("NEW GAME", True, (255,255,255))
    screen.blit(new_game_text, new_game_text.get_rect(center=new_game_rect.center))

    # Back to Menu button
    menu_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        280 + spacing,
        btn_w,
        btn_h,
    )
    hover = menu_rect.collidepoint(mouse)
    pygame.draw.rect(screen, (120,120,120) if hover else (80,80,80), menu_rect)
    pygame.draw.rect(screen, (200,200,200), menu_rect, 2)

    menu_text = msg_font.render("BACK TO MENU", True, (255,255,255))
    screen.blit(menu_text, menu_text.get_rect(center=menu_rect.center))

    return new_game_rect, menu_rect


def draw_trade_menu(mouse):
    screen.fill((30, 30, 30))
    title_font = pygame.font.SysFont(None, 48)
    msg_font = pygame.font.SysFont(None, 28)
    
    title = title_font.render("TRADE ITEMS", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 50)))
    
    buttons = {}
    y_start = 150
    spacing = 60
    btn_w, btn_h = 350, 50

    # Define trade options
    options = [
        ("FOOD_ENERGY", f"Consume Food -> +50% Energy ({inventory['FOOD']})"),
        ("FOOD_LIGHT", f"Food x1 -> +50% Light ({inventory['FOOD']})"),
        ("FOOD_MAP", f"Food x1 -> Map x1 ({inventory['FOOD']}{inventory['MAP']})"),
        ("MAP_ENERGY", f"Map x1 -> +50% Energy ({inventory['MAP']})"),
        ("MAP_LIGHT", f"Map x1 -> +50% Light ({inventory['MAP']})"),
        ("BACK", "Back")
    ]

    for i, (key, label) in enumerate(options):
        rect = pygame.Rect(SCREEN_WIDTH//2 - btn_w//2, y_start + i*spacing, btn_w, btn_h)
        hover = rect.collidepoint(mouse)
        pygame.draw.rect(screen, (120,120,120) if hover else (80,80,80), rect)
        pygame.draw.rect(screen, (200,200,200), rect, 2)
        text = msg_font.render(label, True, (255,255,255))
        screen.blit(text, text.get_rect(center=rect.center))
        buttons[key] = rect
    
    return buttons





def start_new_game():
    global cave, player_x, player_y, map_count
    global light_percentage, energy_percentage, GAME_STATE
    set_level_from_index()
    cave, (cx, cy) = generate_cave(
        WORLD_ROWS, WORLD_COLS, DENSITY, MIN_ROOM_SIZE, MAX_ROOM_SIZE, MAP_NUM, FOOD_NUM, LIGHT_NUM, GATE_NUM
    )

    global enemies
    enemies = []

    floor_cells = [(x, y) for y in range(WORLD_ROWS) for x in range(WORLD_COLS) if cave[y][x] == FLOOR]
    import random
    for _ in range(ENEMY_COUNT):
        if floor_cells:
            ex, ey = random.choice(floor_cells)
            floor_cells.remove((ex, ey))
            enemies.append({
                "x": ex * BASE_CELL_SIZE + BASE_CELL_SIZE // 2,
                "y": ey * BASE_CELL_SIZE + BASE_CELL_SIZE // 2,
                "dir": "right"
            })

    player_x = cx * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    player_y = cy * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    light_percentage = MAX_LIGHT
    energy_percentage = MAX_ENERGY
    map_count = 0
    GAME_STATE = "PLAYING"

def draw_howto():
    screen.fill((30, 30, 30))
    lines = [
        "HOW TO PLAY:",
        "- Arrow Keys: Move your character",
        "- M or MAP button: Toggle map",
        "- Light & Energy decrease over time",
        "- Reach green exit to win",
        "",
        "Click anywhere to return to menu"
    ]
    for i, line in enumerate(lines):
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (50, 50 + i*30))

# ======================
# MAIN LOOP
# ======================

running = True
while running:
    dt = clock.tick(FPS) / 1000
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if GAME_STATE == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_buttons["NEW GAME"].collidepoint(event.pos):
                    start_new_game()
                elif menu_buttons["LEVEL"].collidepoint(event.pos):
                    current_level_index = (current_level_index + 1) % len(LEVELS)
                    set_level_from_index()
                elif menu_buttons["HOW TO PLAY"].collidepoint(event.pos):
                    GAME_STATE = "HOWTO"
                elif menu_buttons["QUIT"].collidepoint(event.pos):
                    running = False

        elif GAME_STATE == "HOWTO":
            if event.type == pygame.MOUSEBUTTONDOWN or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                GAME_STATE = "MENU"

        elif GAME_STATE == "WIN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if win_new_game_button.collidepoint(event.pos):
                    start_new_game()
                elif win_menu_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"

        elif GAME_STATE == "GAMEOVER":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if gameover_new_game_button.collidepoint(event.pos):
                    start_new_game()
                elif gameover_menu_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"
                
        elif GAME_STATE == "TRADE":
            trade_buttons = draw_trade_menu(mouse)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Option 1: Consume food -> Energy
                if trade_buttons["FOOD_ENERGY"].collidepoint(event.pos) and inventory["FOOD"] > 0:
                    inventory["FOOD"] -= 1
                    energy_percentage = min(MAX_ENERGY, energy_percentage + 50)

                # Option 2: Food -> Light
                elif trade_buttons["FOOD_LIGHT"].collidepoint(event.pos) and inventory["FOOD"] > 0:
                    inventory["FOOD"] -= 1
                    light_percentage = min(MAX_LIGHT, light_percentage + 50)

                # Option 3: Food -> Map
                elif trade_buttons["FOOD_MAP"].collidepoint(event.pos) and inventory["FOOD"] > 0:
                    inventory["FOOD"] -= 1
                    inventory["MAP"] += 1
                    map_count += 1

                # Option 4: Map -> Energy
                elif trade_buttons["MAP_ENERGY"].collidepoint(event.pos) and inventory["MAP"] > 0:
                    inventory["MAP"] -= 1
                    map_count = max(0, map_count - 1)
                    energy_percentage = min(MAX_ENERGY, energy_percentage + 50)

                # Option 5: Map -> Light
                elif trade_buttons["MAP_LIGHT"].collidepoint(event.pos) and inventory["MAP"] > 0:
                    inventory["MAP"] -= 1
                    map_count = max(0, map_count - 1)
                    light_percentage = min(MAX_LIGHT, light_percentage + 50)

                # Back to Playing
                elif trade_buttons["BACK"].collidepoint(event.pos):
                    GAME_STATE = "PLAYING"




        elif GAME_STATE == "PLAYING":
            # Toggle map with M key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if show_map:
                    # Always allow closing the map
                    show_map = False

                    # Toggle gates randomly when map is viewed
                    exit_cell = None
                    for y in range(WORLD_ROWS):
                        for x in range(WORLD_COLS):
                            if cave[y][x] == EXIT:
                                exit_cell = (x, y)
                                break
                        if exit_cell:
                            break

                    if exit_cell:
                        rearrange_gates(
                            cave,
                            (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
                            exit_cell,
                            open_ratio=0.5  # half open, half closed
                        )

                elif map_count > 0:
                    show_map = True
                    map_count -= 1
                    inventory["MAP"] -= 1


            # Toggle map with mouse button
            if event.type == pygame.MOUSEBUTTONDOWN:
                if map_button.collidepoint(event.pos):
                    if show_map:
                        # Always allow closing
                        show_map = False

                        # Toggle gates randomly when map is viewed
                        exit_cell = None
                        for y in range(WORLD_ROWS):
                            for x in range(WORLD_COLS):
                                if cave[y][x] == EXIT:
                                    exit_cell = (x, y)
                                    break
                            if exit_cell:
                                break

                        if exit_cell:
                            for rows in cave:
                                print(rows)
                            rearrange_gates(
                                cave,
                                (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
                                exit_cell,
                                open_ratio=0.5  # half open, half closed
                            )
                    elif map_count > 0:
                        # Only open if player has a map
                        show_map = True
                        map_count -= 1
                        inventory["MAP"] -= 1
                elif trade_button.collidepoint(event.pos):
                    GAME_STATE = "TRADE"

                elif not show_map and back_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"


    # ----------------
    # DRAWING & MOVEMENT
    # ----------------
    if GAME_STATE == "MENU":
        menu_buttons = draw_menu(mouse)

    elif GAME_STATE == "HOWTO":
        draw_howto()

    elif GAME_STATE == "WIN":
        win_new_game_button, win_menu_button = draw_win_screen()

    elif GAME_STATE == "GAMEOVER":
        gameover_new_game_button, gameover_menu_button = draw_game_over_screen()

    elif GAME_STATE == "PLAYING":
        keys = pygame.key.get_pressed()
        speed = MIN_MOVE_SPEED + (MAX_MOVE_SPEED - MIN_MOVE_SPEED) * (energy_percentage / 100)

        dx = dy = 0
        moving = False

        if keys[pygame.K_LEFT]:
            dx = -speed * dt; player_direction = "left"; moving = True
        elif keys[pygame.K_RIGHT]:
            dx = speed * dt; player_direction = "right"; moving = True
        elif keys[pygame.K_UP]:
            dy = -speed * dt; player_direction = "up"; moving = True
        elif keys[pygame.K_DOWN]:
            dy = speed * dt; player_direction = "down"; moving = True

        if can_move_pixel(player_x + dx, player_y):
            player_x += dx
        if can_move_pixel(player_x, player_y + dy):
            player_y += dy

        if moving:
            animation_timer += dt
            if animation_timer >= ANIM_SPEED:
                animation_timer = 0
                animation_frame = (animation_frame + 1) % FRAMES
        else:
            animation_frame = 0

        # Decrease light and energy
        light_percentage = max(MIN_LIGHT, light_percentage - LIGHT_DRAIN_PER_SEC * dt)
        energy_percentage = max(MIN_ENERGY, energy_percentage - ENERGY_DRAIN_PER_SEC * dt)
        if energy_percentage <= 0:
            GAME_STATE = "GAMEOVER"


        # --------------------------
        # ITEM COLLECTION LOGIC
        # --------------------------
        px_cell = int(player_x // BASE_CELL_SIZE)
        py_cell = int(player_y // BASE_CELL_SIZE)

        if cave[py_cell][px_cell] in (LIGHT, FOOD, MAP, EXIT):
            item = cave[py_cell][px_cell]
            cave[py_cell][px_cell] = FLOOR  # Remove the item from the cave

            if item == EXIT:
                GAME_STATE = "WIN"
            elif item == LIGHT:
                light_percentage = min(MAX_LIGHT, light_percentage + 50)
            elif item == FOOD:
                if energy_percentage > 50:
                    # Store in inventory
                    inventory["FOOD"] += 1
                else:
                    # Consume immediately
                    energy_percentage = min(MAX_ENERGY, energy_percentage + 50)
            elif item == MAP:
                if energy_percentage > 50:
                    inventory["MAP"] += 1
                    map_count += 1
                else:
                    map_count += 10

                

        # Drawing
        screen.fill(BLACK)
        if show_map:
            draw_map(screen, cave,
                     (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
                     (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            draw_world()
            draw_light_overlay()
            draw_bar(10, SCREEN_HEIGHT - 70, energy_percentage, "Energy", (100, 200, 255))
            back_button = draw_back_button()

        # --------------------------
        # ENEMY LOGIC
        # --------------------------
        for enemy in enemies:
            if light_percentage >= ENEMY_TRIGGER_LIGHT:
                dx = player_x - enemy["x"]
                dy = player_y - enemy["y"]
                dist = (dx**2 + dy**2) ** 0.5
                if dist != 0:
                    move_dist = ENEMY_SPEED * dt
                    step_x = dx / dist * move_dist
                    step_y = dy / dist * move_dist

                    # Update facing direction by horizontal intent
                    if step_x > 0:
                        enemy["dir"] = "right"
                    elif step_x < 0:
                        enemy["dir"] = "left"

                    # Move separately in x and y, checking collisions
                    if can_move_pixel(enemy["x"] + step_x, enemy["y"]):
                        enemy["x"] += step_x
                    if can_move_pixel(enemy["x"], enemy["y"] + step_y):
                        enemy["y"] += step_y

                # Collision with player
                if abs(enemy["x"] - player_x) < player_radius and abs(enemy["y"] - player_y) < player_radius:
                    GAME_STATE = "GAMEOVER"


        map_button = draw_map_button()
        trade_button = draw_trade_button()
        draw_inventory()

    pygame.display.flip()

pygame.quit()
