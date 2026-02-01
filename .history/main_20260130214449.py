import pygame
import time
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
        MAP_NUM = 300
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
click_sfx = pygame.mixer.Sound("assets/sounds/click.wav")
click_sfx.set_volume(0.3)
reward_sfx = pygame.mixer.Sound("assets/sounds/reward.mp3")
reward_sfx.set_volume(0.3)
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

map_btn_img = pygame.image.load("assets/buttons/map_btn.jpg").convert_alpha()
trade_btn_img = pygame.image.load("assets/buttons/inventory.jpg").convert_alpha()
back_btn_img = pygame.image.load("assets/buttons/back_btn.jpg").convert_alpha()

# Optional: scale to fit the button size
map_btn_img = pygame.transform.scale(map_btn_img, (80, 80))
trade_btn_img = pygame.transform.scale(trade_btn_img, (80, 80))
back_btn_img = pygame.transform.scale(back_btn_img, (80, 80))


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

# Background
menu_bg = pygame.image.load("assets/shadow_of_death_menu.png").convert()
menu_bg = pygame.transform.scale(menu_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))


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

def find_exit_cell():
    for y in range(WORLD_ROWS):
        for x in range(WORLD_COLS):
            if cave[y][x] == EXIT:
                return (x, y)
    return None


# ======================
# UI ELEMENTS
# ======================

def draw_map_button():
    rect = pygame.Rect(SCREEN_WIDTH - 100, 10, 80, 80)

    # Button frame (optional but recommended)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)

    screen.blit(map_btn_img, rect.topleft)
    return rect


def draw_trade_button():
    rect = pygame.Rect(SCREEN_WIDTH - 190, 10, 80, 80)

    # Button frame
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)

    screen.blit(trade_btn_img, rect.topleft)
    return rect



def draw_bar(x, y, value, label, color):
    w, h = 200, 20
    pygame.draw.rect(screen, (50, 50, 50), (x, y, w, h))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h), 2)
    pygame.draw.rect(screen, color, (x, y, int(w * value / 100), h))
    txt = font.render(f"{label}: {int(value)}%", True, (255, 255, 255))
    screen.blit(txt, (x + w + 10, y + 3))

def draw_back_button():
    rect = pygame.Rect(10, 10, 80, 80)

    # Button frame
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)

    screen.blit(back_btn_img, rect.topleft)
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
    # ---------- FULL BACKGROUND IMAGE ----------
    screen.blit(menu_bg, (0, 0))

    # ---------- RIGHT PANEL ----------
    panel_width = 420
    panel_x = SCREEN_WIDTH - panel_width

    # panel_surface = pygame.Surface((panel_width, SCREEN_HEIGHT))
    # panel_surface.fill((25, 25, 25))
    # panel_surface.set_alpha(240)  # Slight transparency
    # screen.blit(panel_surface, (panel_x, 0))

    # # ---------- GAME TITLE (on left side) ----------
    # title_font = pygame.font.SysFont(None, 64)
    # title = title_font.render("SHADOW OF DEATH", True, (240, 240, 240))
    # screen.blit(title, (60, 80))  # Left side like artwork

    # ---------- BUTTONS ----------
    buttons = {}
    w, h = 260, 60
    start_y = 220
    spacing = 80

    labels = ["NEW GAME", "LEVEL", "HOW TO PLAY", "QUIT"]

    for i, label in enumerate(labels):
        rect = pygame.Rect(
            panel_x + panel_width // 2 - w // 2,
            start_y + 120 + i * spacing,
            w,
            h
        )

        hover = rect.collidepoint(mouse)

        # ---------- BUTTON BACKGROUND ----------
        base_color  = (120, 90, 30)
        hover_color = (160, 120, 40)
        color = hover_color if hover else base_color

        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=10)

        # Main button
        pygame.draw.rect(screen, color, rect, border_radius=10)

        # Border
        pygame.draw.rect(screen, (180, 180, 180), rect, 2, border_radius=10)

        # ---------- BUTTON TEXT ----------
        if label == "LEVEL":
            text_label = f"LEVEL: {LEVEL.upper()}"
        else:
            text_label = label

        text = font.render(text_label, True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

        buttons[label] = rect

    return buttons



def draw_win_screen():
    # ---------- LOAD & DRAW BACKGROUND IMAGE ----------
    win_bg = pygame.image.load("assets/win_screen.png").convert()
    win_bg = pygame.transform.scale(win_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(win_bg, (0, 0))

    # ---------- DARK OVERLAY FOR READABILITY ----------
    # overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # overlay.set_alpha(120)  # adjust if text is too dark/light
    # overlay.fill((0, 0, 0))
    # screen.blit(overlay, (0, 0))

    # ---------- TEXT ----------
    # title_font = pygame.font.SysFont(None, 64)
    msg_font = pygame.font.SysFont(None, 28)

    # title = title_font.render("YOU ESCAPED!", True, (255, 215, 120))
    # subtitle = msg_font.render(
    #     "Congratulations, you found the exit.",
    #     True,
    #     (230, 230, 230),
    # )

    # screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 140)))
    # screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 190)))

    # ---------- BUTTONS ----------
    btn_w, btn_h = 260, 60
    spacing = 80
    mouse = pygame.mouse.get_pos()

    base_color = (85, 88, 92)
    hover_color = (115, 118, 122)
    border_color = (200, 170, 80)

    # NEW GAME
    new_game_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        450,
        btn_w,
        btn_h,
    )

    pygame.draw.rect(
        screen,
        hover_color if new_game_rect.collidepoint(mouse) else base_color,
        new_game_rect,
        border_radius=8,
    )
    pygame.draw.rect(screen, border_color, new_game_rect, 2, border_radius=8)

    new_game_text = msg_font.render("NEW GAME", True, (255, 255, 255))
    screen.blit(new_game_text, new_game_text.get_rect(center=new_game_rect.center))

    # BACK TO MENU
    menu_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        450 + spacing,
        btn_w,
        btn_h,
    )

    pygame.draw.rect(
        screen,
        hover_color if menu_rect.collidepoint(mouse) else base_color,
        menu_rect,
        border_radius=8,
    )
    pygame.draw.rect(screen, border_color, menu_rect, 2, border_radius=8)

    menu_text = msg_font.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(menu_text, menu_text.get_rect(center=menu_rect.center))

    return new_game_rect, menu_rect



def draw_game_over_screen():
    # ---------- LOAD & DRAW BACKGROUND IMAGE ----------
    game_over_bg = pygame.image.load("assets/game_over_screen.png").convert()
    game_over_bg = pygame.transform.scale(game_over_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(game_over_bg, (0, 0))

    # ---------- DARK OVERLAY ----------
    # overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    # overlay.set_alpha(150)  # slightly darker than win screen
    # overlay.fill((0, 0, 0))
    # screen.blit(overlay, (0, 0))

    # ---------- TEXT ----------
    # title_font = pygame.font.SysFont(None, 64)
    msg_font = pygame.font.SysFont(None, 28)

    # title = title_font.render("GAME OVER", True, (220, 90, 90))
    # subtitle = msg_font.render(
    #     "You ran out of energy.",
    #     True,
    #     (210, 210, 210),
    # )

    # screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 140)))
    # screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 190)))

    # ---------- BUTTON STYLING ----------
    base_color   = (85, 88, 92)     # dark silver
    hover_color  = (115, 118, 122)  # lighter silver
    border_color = (200, 170, 80)   # gold

    btn_w, btn_h = 260, 60
    spacing = 80
    mouse = pygame.mouse.get_pos()

    # ---------- NEW GAME ----------
    new_game_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        280,
        btn_w,
        btn_h,
    )

    pygame.draw.rect(
        screen,
        hover_color if new_game_rect.collidepoint(mouse) else base_color,
        new_game_rect,
        border_radius=8,
    )
    pygame.draw.rect(screen, border_color, new_game_rect, 2, border_radius=8)

    new_game_text = msg_font.render("NEW GAME", True, (255, 255, 255))
    screen.blit(new_game_text, new_game_text.get_rect(center=new_game_rect.center))

    # ---------- BACK TO MENU ----------
    menu_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - btn_w // 2,
        280 + spacing,
        btn_w,
        btn_h,
    )

    pygame.draw.rect(
        screen,
        hover_color if menu_rect.collidepoint(mouse) else base_color,
        menu_rect,
        border_radius=8,
    )
    pygame.draw.rect(screen, border_color, menu_rect, 2, border_radius=8)

    menu_text = msg_font.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(menu_text, menu_text.get_rect(center=menu_rect.center))

    return new_game_rect, menu_rect


def draw_trade_window(mouse):
    window_w, window_h = 420, 460
    window_x = SCREEN_WIDTH // 2 - window_w // 2
    window_y = SCREEN_HEIGHT // 2 - window_h // 2

    # Window background
    pygame.draw.rect(screen, (40, 40, 40), (window_x, window_y, window_w, window_h))
    pygame.draw.rect(screen, (200, 200, 200), (window_x, window_y, window_w, window_h), 2)

    title_font = pygame.font.SysFont(None, 36)
    msg_font = pygame.font.SysFont(None, 24)

    title = title_font.render("TRADE", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, window_y + 30)))


    # ---------- INVENTORY DISPLAY ----------
    food_icon = pygame.image.load("assets/food.jpg").convert_alpha()
    map_icon  = pygame.image.load("assets/map.jpg").convert_alpha()

    inv_y = window_y + 70
    icon_size = 64
    spacing = 120

    # Food
    food_icon_scaled = pygame.transform.scale(food_icon, (icon_size, icon_size))
    food_x = SCREEN_WIDTH // 2 - spacing
    screen.blit(food_icon_scaled, (food_x, inv_y))
    food_text = msg_font.render(f"x {inventory['FOOD']}", True, (255, 255, 255))
    screen.blit(food_text, (food_x + icon_size + 8, inv_y + 20))

    # Map
    map_icon_scaled = pygame.transform.scale(map_icon, (icon_size, icon_size))
    map_x = SCREEN_WIDTH // 2 + spacing // 2
    screen.blit(map_icon_scaled, (map_x, inv_y))
    map_text = msg_font.render(f"x {inventory['MAP']}", True, (255, 255, 255))
    screen.blit(map_text, (map_x + icon_size + 8, inv_y + 20))

    buttons = {}
    y_start = window_y + 160
    spacing = 45
    btn_w, btn_h = window_w - 40, 36

    options = [
        ("FOOD_ENERGY", f"Consume Food → +50% Energy"),
        ("FOOD_LIGHT",  f"Food → +50% Light"),
        ("FOOD_MAP",    f"Food → Map"),
        ("MAP_ENERGY",  f"Map → +50% Energy"),
        ("MAP_LIGHT",   f"Map → +50% Light"),
        ("BACK",        "Done")
    ]

    for i, (key, label) in enumerate(options):
        rect = pygame.Rect(window_x + 20, y_start + i*spacing, btn_w, btn_h)
        hover = rect.collidepoint(mouse)

        pygame.draw.rect(screen, (110,110,110) if hover else (70,70,70), rect)
        pygame.draw.rect(screen, (180,180,180), rect, 2)

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

font_title = pygame.font.SysFont(None, 64)
font_medium = pygame.font.SysFont(None, 48)
font_text  = pygame.font.SysFont(None, 28)
font_small = pygame.font.SysFont(None, 24)
# How To Play text
HOW_TO_PLAY_TEXT = [
    "🎯 OBJECTIVE",
    "Escape the cave by reaching the exit. Explore carefully, collect resources, manage your energy and light, and survive the monsters lurking in the darkness.Use the arrow keys to move the player up, down, left and right",
    "",

    "🗺️ ITEMS YOU CAN FIND",
    "Map",
    "- Adds a map to your inventory.",
    "- Each map can be used once when collected.",
    "- Using a map reveals the cave layout but rearranges the doors, opening new paths.",
    "- Maps can also be traded for energy or light.",
    "",
    "Food",
    "- Restores 50% energy when consumed.",
    "- If your energy is above 50%, food is stored in your inventory instead.",
    "- Stored food can be traded for maps or light.",
    "",
    "Light",
    "- Increases visibility in the cave.",
    "- High light attracts monsters.",
    "- Light can be traded for food or maps.",
    "",

    "⚡ PLAYER STATS",
    "Energy",
    "- Decreases over time.",
    "- Affects movement speed.",
    "- If energy reaches zero, the game is over.",
    "",
    "Speed",
    "- Directly linked to energy level.",
    "- Higher energy means faster movement.",
    "",
    "Light",
    "- Controls how much of the cave you can see.",
    "- Too little light makes navigation dangerous.",
    "- Too much light attracts enemies.",
    "",

    "💱 TRADING",
    "- Trade items through the inventory menu.",
    "- Every trade has a cost—choose wisely.",
    "Examples:",
    "- Food → Energy or Light",
    "- Map → Energy or Light",
    "",

    "🐉 ENEMIES",
    "- Monsters remain still in low light.",
    "- When light is high, they hunt you.",
    "- Avoid them—contact means instant death.",
    "",

    "⚠️ SURVIVAL TIPS",
    "- Use maps strategically; doors change every time.",
    "- Balance light carefully to avoid monsters.",
    "- Manage energy to maintain speed.",
    "- Smart trading can save your life.",
    "",

    "🏁 WINNING",
    "Reach the exit while staying alive. Planning, balance, and smart decisions are the key to escaping the cave."
]


# ---------- GLOBALS FOR SCROLL ----------
# ---------- GLOBALS ----------
# ---------- GLOBALS FOR SCROLL ----------
how_to_scroll = 0  # current scroll offset
scroll_speed = 40  # pixels per scroll
max_scroll = 0     # calculated dynamically
header_bottom_gap = 30  # extra space below headers
top_padding = 0         # space above first line of text
bottom_padding = 20      # space below last line of text

def draw_how_to_play(mouse, scroll_delta=0):
    global how_to_scroll, max_scroll

    screen.fill((20, 20, 20))  # dark background

    # ---------- PANEL ----------
    panel_width = 1000
    panel_height = SCREEN_HEIGHT - 150
    panel_x = (SCREEN_WIDTH - panel_width) // 2
    panel_y = 100
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (35, 35, 35), panel_rect)
    pygame.draw.rect(screen, (180, 180, 180), panel_rect, 2)

    # ---------- PANEL TITLE ----------
    title_surf = font_title.render("HOW TO PLAY", True, (240, 240, 240))
    screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50)))

    # ---------- SCROLL ----------
    how_to_scroll += scroll_delta * scroll_speed

    # ---------- CREATE CLIPPED SURFACE ----------
    text_surface = pygame.Surface((panel_width - 50, panel_height - 50 - top_padding - bottom_padding))
    text_surface.fill((35, 35, 35))
    
    # enable alpha for transparency
    text_surface.set_colorkey((0, 0, 0))

    y_offset = top_padding + how_to_scroll  # start from top of clipped surface
    line_spacing = 42
    max_text_width = panel_width - 40
    total_text_height = 0

    for line in HOW_TO_PLAY_TEXT:
        is_header = line.strip() != "" and (line.endswith(":") or line[0] in "🎯🗺️⚡💱🐉⚠️🏁")
        font = font_medium if is_header else font_text

        if is_header:
            y_offset += header_bottom_gap
            total_text_height += header_bottom_gap

        words = line.split(' ')
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            test_surf = font.render(test_line, True, (255, 255, 255))
            if test_surf.get_width() > max_text_width:
                text_surface.blit(font.render(current_line, True, (255, 255, 255)), (0, y_offset))
                y_offset += line_spacing
                total_text_height += line_spacing
                current_line = word + " "
            else:
                current_line = test_line

        if current_line.strip() != "":
            text_surface.blit(font.render(current_line, True, (255, 255, 255)), (0, y_offset))
            y_offset += line_spacing
            total_text_height += line_spacing

        if is_header:
            y_offset += header_bottom_gap
            total_text_height += header_bottom_gap

    # ---------- CALCULATE MAX SCROLL ----------
    visible_text_height = panel_height - 50 - top_padding - bottom_padding
    if total_text_height > visible_text_height:
        max_scroll = visible_text_height - total_text_height
    else:
        max_scroll = 0

    # clamp scroll
    how_to_scroll = max(min(how_to_scroll, 0), max_scroll)

    # ---------- BLIT CLIPPED SURFACE ----------
    screen.blit(text_surface, (panel_x + 20, panel_y + 50), area=pygame.Rect(0, 0, panel_width - 40, visible_text_height))

    # ---------- BACK BUTTON ----------
    btn_w, btn_h = 150, 50
    btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, SCREEN_HEIGHT - 70, btn_w, btn_h)
    hover = btn_rect.collidepoint(mouse)
    pygame.draw.rect(screen, (110, 110, 110) if hover else (70, 70, 70), btn_rect, border_radius=8)
    pygame.draw.rect(screen, (180, 180, 180), btn_rect, 2, border_radius=8)
    text_btn = font_small.render("BACK", True, (255, 255, 255))
    screen.blit(text_btn, text_btn.get_rect(center=btn_rect.center))

    return btn_rect



# ======================
# MAIN LOOP
# ======================

scroll_y=0
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
                    click_sfx.play()
                elif menu_buttons["LEVEL"].collidepoint(event.pos):
                    current_level_index = (current_level_index + 1) % len(LEVELS)
                    set_level_from_index()
                    click_sfx.play()
                elif menu_buttons["HOW TO PLAY"].collidepoint(event.pos):
                    GAME_STATE = "HOWTO"
                    click_sfx.play()
                elif menu_buttons["QUIT"].collidepoint(event.pos):
                    click_sfx.play()
                    time.sleep(0.2)
                    running = False

        elif GAME_STATE == "HOWTO":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # scroll up
                    draw_how_to_play(pygame.mouse.get_pos(), scroll_delta=1)
                elif event.button == 5:  # scroll down
                    draw_how_to_play(pygame.mouse.get_pos(), scroll_delta=-1)
                elif back_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"
                    click_sfx.play()

        elif GAME_STATE == "WIN":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if win_new_game_button.collidepoint(event.pos):
                    start_new_game()
                    click_sfx.play()
                elif win_menu_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"
                    click_sfx.play()

        elif GAME_STATE == "GAMEOVER":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if gameover_new_game_button.collidepoint(event.pos):
                    start_new_game()
                    click_sfx.play()
                elif gameover_menu_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"
                    click_sfx.play()
                
        elif GAME_STATE == "TRADE":
            trade_buttons = draw_trade_window(mouse)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if trade_buttons["FOOD_ENERGY"].collidepoint(event.pos) and inventory["FOOD"] > 0:
                    click_sfx.play()
                    inventory["FOOD"] -= 1
                    energy_percentage = min(MAX_ENERGY, energy_percentage + 50)
                elif trade_buttons["FOOD_LIGHT"].collidepoint(event.pos) and inventory["FOOD"] > 0:
                    click_sfx.play()
                    inventory["FOOD"] -= 1
                    light_percentage = min(MAX_LIGHT, light_percentage + 50)
                elif trade_buttons["FOOD_MAP"].collidepoint(event.pos) and inventory["FOOD"] > 0:
                    click_sfx.play()
                    inventory["FOOD"] -= 1
                    inventory["MAP"] += 1
                    map_count += 1
                elif trade_buttons["MAP_ENERGY"].collidepoint(event.pos) and inventory["MAP"] > 0:
                    click_sfx.play()
                    inventory["MAP"] -= 1
                    map_count = max(0, map_count - 1)
                    energy_percentage = min(MAX_ENERGY, energy_percentage + 50)
                elif trade_buttons["MAP_LIGHT"].collidepoint(event.pos) and inventory["MAP"] > 0:
                    click_sfx.play()
                    inventory["MAP"] -= 1
                    map_count = max(0, map_count - 1)
                    light_percentage = min(MAX_LIGHT, light_percentage + 50)
                elif trade_buttons["BACK"].collidepoint(event.pos):
                    click_sfx.play()
                    GAME_STATE = "PLAYING"

        elif GAME_STATE == "MAP":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                exit_cell = find_exit_cell()
                if exit_cell:
                    rearrange_gates(
                        cave,
                        (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
                        exit_cell,
                        open_ratio=0.5
                    )
                GAME_STATE = "PLAYING"

            if event.type == pygame.MOUSEBUTTONDOWN:
                if map_button.collidepoint(event.pos):
                    click_sfx.play()
                    exit_cell = find_exit_cell()
                    if exit_cell:
                        rearrange_gates(
                            cave,
                            (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
                            exit_cell,
                            open_ratio=0.5
                        )
                    GAME_STATE = "PLAYING"


        elif GAME_STATE == "PLAYING":
            # Toggle map with M key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if inventory["MAP"] > 0:
                    inventory["MAP"] -= 1
                    map_count = max(0, map_count - 1)
                    GAME_STATE = "MAP"


            # Toggle map with mouse button
            if event.type == pygame.MOUSEBUTTONDOWN:
                if map_button.collidepoint(event.pos) and inventory["MAP"] > 0:
                    click_sfx.play()
                    inventory["MAP"] -= 1
                    map_count = max(0, map_count - 1)
                    GAME_STATE = "MAP"
                elif trade_button.collidepoint(event.pos):
                    GAME_STATE = "TRADE"
                    click_sfx.play()

                elif back_button.collidepoint(event.pos):
                    GAME_STATE = "MENU"
                    click_sfx.play()


    # ----------------
    # DRAWING & MOVEMENT
    # ----------------
    if GAME_STATE == "MENU":
        menu_buttons = draw_menu(mouse)

    elif GAME_STATE == "HOWTO":
        back_button = draw_how_to_play(mouse, scroll_y)

    elif GAME_STATE == "WIN":
        win_new_game_button, win_menu_button = draw_win_screen()

    elif GAME_STATE == "GAMEOVER":
        gameover_new_game_button, gameover_menu_button = draw_game_over_screen()

    elif GAME_STATE == "MAP":
        draw_map(
            screen,
            cave,
            (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        map_button = draw_map_button()


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
            reward_sfx.play()
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
        draw_world()
        draw_light_overlay()
        draw_bar(10, SCREEN_HEIGHT - 70, energy_percentage, "Energy", (255, 120, 120))
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

    pygame.display.flip()

pygame.quit()
