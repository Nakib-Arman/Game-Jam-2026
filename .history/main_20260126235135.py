import pygame
from cave import generate_cave
from map import draw_map

# ======================
# CONFIGURATION
# ======================

LEVELS = ["easy", "medium", "hard"]
current_level_index = 0
LEVEL = LEVELS[current_level_index]

def set_level_from_index():
    global LEVEL, WORLD_ROWS, WORLD_COLS, MAP_NUM, FOOD_NUM, LIGHT_NUM
    LEVEL = LEVELS[current_level_index]
    if LEVEL == "easy":
        WORLD_ROWS = 46
        WORLD_COLS = 50
        MAP_NUM = 3
        FOOD_NUM = 8
        LIGHT_NUM = 8
    elif LEVEL == "medium":
        WORLD_ROWS = 71
        WORLD_COLS = 75
        MAP_NUM = 6
        FOOD_NUM = 16
        LIGHT_NUM = 16
    elif LEVEL == "hard":
        WORLD_ROWS = 96
        WORLD_COLS = 100
        MAP_NUM = 12
        FOOD_NUM = 32
        LIGHT_NUM = 32

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
# TILE CONSTANTS
# ======================

WALL = 1
FLOOR = 0
EXIT = 2
MAP = 3
FOOD = 4
LIGHT = 5

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
big_font = pygame.font.SysFont(None, 64)

wall_image = pygame.image.load("assets/wall_block.jpg")
wall_image = pygame.transform.scale(wall_image, (BASE_CELL_SIZE, BASE_CELL_SIZE))

# ======================
# GAME STATE
# ======================

GAME_STATE = "MENU"  # MENU, PLAYING, HOWTO, WIN

cave = None
player_x = player_y = 0
player_radius = BASE_CELL_SIZE // 4

player_direction = "down"
animation_frame = 0
animation_timer = 0
ANIM_SPEED = 0.15

light_percentage = MAX_LIGHT
energy_percentage = MAX_ENERGY
map_count = 0
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
            if cave[cy][cx] == WALL:
                return False
    return True

def get_camera_offset():
    cam_x = player_x - SCREEN_WIDTH // 2
    cam_y = player_y - SCREEN_HEIGHT // 2
    cam_x = max(0, min(cam_x, WORLD_COLS * BASE_CELL_SIZE - SCREEN_WIDTH))
    cam_y = max(0, min(cam_y, WORLD_ROWS * BASE_CELL_SIZE - SCREEN_HEIGHT))
    return int(cam_x), int(cam_y)

# ======================
# UI
# ======================

def draw_bar(x, y, value, label, color):
    w, h = 200, 20
    pygame.draw.rect(screen, (50, 50, 50), (x, y, w, h))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, w, h), 2)
    pygame.draw.rect(screen, color, (x, y, int(w * value / 100), h))
    txt = font.render(f"{label}: {int(value)}%", True, (255, 255, 255))
    screen.blit(txt, (x + w + 10, y + 3))

def draw_win_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = big_font.render("Congratulations!", True, (255, 255, 255))
    sub = font.render("You've won the game", True, (200, 200, 200))
    hint = font.render("Click or press ESC to return to menu", True, (180, 180, 180))

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)))
    screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
    screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40)))

# ======================
# MENU
# ======================

def draw_menu(mouse):
    screen.fill((20, 20, 20))
    title = big_font.render("CAVE EXPLORER", True, (240, 240, 240))
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

        text_label = f"LEVEL: {LEVEL.upper()}" if label == "LEVEL" else label
        txt = font.render(text_label, True, (255,255,255))
        screen.blit(txt, txt.get_rect(center=rect.center))
        buttons[label] = rect
    return buttons

def start_new_game():
    global cave, player_x, player_y, map_count
    global light_percentage, energy_percentage, GAME_STATE
    set_level_from_index()
    cave, (cx, cy) = generate_cave(
        WORLD_ROWS, WORLD_COLS, DENSITY,
        MIN_ROOM_SIZE, MAX_ROOM_SIZE,
        MAP_NUM, FOOD_NUM, LIGHT_NUM
    )
    player_x = cx * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    player_y = cy * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    light_percentage = MAX_LIGHT
    energy_percentage = MAX_ENERGY
    map_count = 0
    GAME_STATE = "PLAYING"

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

        elif GAME_STATE == "WIN":
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                GAME_STATE = "MENU"

    if GAME_STATE == "MENU":
        menu_buttons = draw_menu(mouse)

    elif GAME_STATE == "PLAYING":
        keys = pygame.key.get_pressed()
        speed = MAX_MOVE_SPEED * (energy_percentage / 100)

        dx = dy = 0
        if keys[pygame.K_LEFT]: dx = -speed * dt
        if keys[pygame.K_RIGHT]: dx = speed * dt
        if keys[pygame.K_UP]: dy = -speed * dt
        if keys[pygame.K_DOWN]: dy = speed * dt

        if can_move_pixel(player_x + dx, player_y): player_x += dx
        if can_move_pixel(player_x, player_y + dy): player_y += dy

        light_percentage = max(MIN_LIGHT, light_percentage - LIGHT_DRAIN_PER_SEC * dt)
        energy_percentage = max(MIN_ENERGY, energy_percentage - ENERGY_DRAIN_PER_SEC * dt)

        px = int(player_x // BASE_CELL_SIZE)
        py = int(player_y // BASE_CELL_SIZE)

        if cave[py][px] == EXIT:
            GAME_STATE = "WIN"

        screen.fill(BLACK)
        draw_bar(10, SCREEN_HEIGHT - 40, energy_percentage, "Energy", (100,200,255))

    elif GAME_STATE == "WIN":
        draw_win_screen()

    pygame.display.flip()

pygame.quit()
