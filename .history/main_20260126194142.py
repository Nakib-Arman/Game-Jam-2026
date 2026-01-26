import pygame
import random
from cave import generate_cave
from map import draw_map

# ======================
# CONFIGURATION
# ======================

LEVELS = ["easy", "medium", "hard"]
current_level_index = 0
LEVEL = LEVELS[current_level_index]

def set_level_from_index():
    global LEVEL, WORLD_ROWS, WORLD_COLS
    LEVEL = LEVELS[current_level_index]
    if LEVEL == "easy":
        WORLD_ROWS = 46
        WORLD_COLS = 50
    elif LEVEL == "medium":
        WORLD_ROWS = 71
        WORLD_COLS = 75
    elif LEVEL == "hard":
        WORLD_ROWS = 96
        WORLD_COLS = 100

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
# INIT
# ======================

pygame.init()
SCREEN_WIDTH = VIEW_COLS * BASE_CELL_SIZE
SCREEN_HEIGHT = VIEW_ROWS * BASE_CELL_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cave Explorer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

wall_image = pygame.image.load("assets/wall_block.png")
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

show_map = False
map_unlocked = False

# ======================
# ITEMS
# ======================

items = []  # Will hold dictionaries with keys: type, x, y, collected
ITEM_TYPES = ["food", "light", "map"]
NUM_ITEMS = 15  # total number of items

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
            if cave[cy][cx] == 1:
                return False
    return True

def get_camera_offset():
    cam_x = player_x - SCREEN_WIDTH // 2
    cam_y = player_y - SCREEN_HEIGHT // 2
    cam_x = max(0, min(cam_x, WORLD_COLS * BASE_CELL_SIZE - SCREEN_WIDTH))
    cam_y = max(0, min(cam_y, WORLD_ROWS * BASE_CELL_SIZE - SCREEN_HEIGHT))
    return int(cam_x), int(cam_y)

def place_items():
    global items
    items = []
    placed = 0
    while placed < NUM_ITEMS:
        x = random.randint(0, WORLD_COLS - 1)
        y = random.randint(0, WORLD_ROWS - 1)
        if cave[y][x] == 0 and all(item["x"] != x or item["y"] != y for item in items):
            item_type = random.choice(ITEM_TYPES)
            items.append({"type": item_type, "x": x, "y": y, "collected": False})
            placed += 1

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

            if cave[wy][wx] == 1:
                screen.blit(wall_image, (sx, sy))
            else:
                pygame.draw.rect(
                    screen, LIGHT_GRAY,
                    (sx, sy, BASE_CELL_SIZE, BASE_CELL_SIZE)
                )

    # Draw items in the visible portion
    for item in items:
        if item["collected"]:
            continue
        ix = item["x"] * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
        iy = item["y"] * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
        screen_x = ix - cam_x
        screen_y = iy - cam_y
        if item["type"] == "food":
            color = (255, 100, 100)
        elif item["type"] == "light":
            color = (255, 255, 100)
        elif item["type"] == "map":
            color = (100, 255, 100)
        pygame.draw.circle(screen, color, (screen_x, screen_y), BASE_CELL_SIZE // 4)

    # Draw player
    sprite = sprites[player_direction][animation_frame]
    screen.blit(
        sprite,
        sprite.get_rect(center=(player_x - cam_x, player_y - cam_y))
    )

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

def start_new_game():
    global cave, player_x, player_y, light_percentage, energy_percentage, GAME_STATE, items, map_unlocked
    set_level_from_index()
    cave, (cx, cy) = generate_cave(
        WORLD_ROWS, WORLD_COLS, DENSITY, MIN_ROOM_SIZE, MAX_ROOM_SIZE
    )
    player_x = cx * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    player_y = cy * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    light_percentage = MAX_LIGHT
    energy_percentage = MAX_ENERGY
    GAME_STATE = "PLAYING"
    map_unlocked = False
    place_items()  # Randomly place items for this game

def draw_howto():
    screen.fill((30, 30, 30))
    lines = [
        "HOW TO PLAY:",
        "- Arrow Keys: Move your character",
        "- M or MAP button: Toggle map",
        "- Light & Energy decrease over time",
        "- Reach green exit to win",
        "- Collect FOOD to restore energy",
        "- Collect LIGHT to restore light",
        "- Collect MAP to reveal the map",
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

        elif GAME_STATE == "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m and map_unlocked:
                show_map = not show_map
            if event.type == pygame.MOUSEBUTTONDOWN:
                if map_button.collidepoint(event.pos) and map_unlocked:
                    show_map = not show_map
                elif not show_map and back_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"

    # ----------------
    # UPDATE & DRAW
    # ----------------
    if GAME_STATE == "MENU":
        menu_buttons = draw_menu(mouse)

    elif GAME_STATE == "HOWTO":
        draw_howto()

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

        # Check item collection
        player_tile_x = int(player_x // BASE_CELL_SIZE)
        player_tile_y = int(player_y // BASE_CELL_SIZE)
        for item in items:
            if item["collected"]:
                continue
            if item["x"] == player_tile_x and item["y"] == player_tile_y:
                item["collected"] = True
                if item["type"] == "food":
                    energy_percentage = min(MAX_ENERGY, energy_percentage + 25)
                elif item["type"] == "light":
                    light_percentage = min(MAX_LIGHT, light_percentage + 25)
                elif item["type"] == "map":
                    map_unlocked = True
                    show_map = True

        if moving:
            animation_timer += dt
            if animation_timer >= ANIM_SPEED:
                animation_timer = 0
                animation_frame = (animation_frame + 1) % FRAMES
        else:
            animation_frame = 0

        light_percentage = max(MIN_LIGHT, light_percentage - LIGHT_DRAIN_PER_SEC * dt)
        energy_percentage = max(MIN_ENERGY, energy_percentage - ENERGY_DRAIN_PER_SEC * dt)

        screen.fill(BLACK)
        if show_map and map_unlocked:
            draw_map(screen, cave,
                     (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
                     (SCREEN_WIDTH, SCREEN_HEIGHT))
            # Draw items on the map
            map_width = SCREEN_WIDTH
            map_height = SCREEN_HEIGHT
            tile_w = map_width / WORLD_COLS
            tile_h = map_height / WORLD_ROWS
            for item in items:
                if item["collected"]:
                    continue
                color = (255, 100, 100) if item["type"]=="food" else \
                        (255, 255, 100) if item["type"]=="light" else \
                        (100, 255, 100)
                map_x = int(item["x"] * tile_w)
                map_y = int(item["y"] * tile_h)
                pygame.draw.rect(screen, color, (map_x, map_y, tile_w, tile_h))
        else:
            draw_world()
            draw_light_overlay()
            draw_bar(10, SCREEN_HEIGHT - 70, energy_percentage, "Energy", (100, 200, 255))
            draw_bar(10, SCREEN_HEIGHT - 40, light_percentage, "Light", (240, 240, 100))
            back_button = draw_back_button()

        map_button = draw_map_button()

    pygame.display.flip()

pygame.quit()
