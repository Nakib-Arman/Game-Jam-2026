import pygame
from cave import generate_cave
from map import draw_map


LEVEL = "easy"

if(LEVEL == "easy"):
    WORLD_ROWS = 46
    WORLD_COLS = 50
elif(LEVEL == "medium"):
    WORLD_ROWS = 66
    WORLD_COLS = 70
elif(LEVEL == "hard"):
    WORLD_ROWS = 86
    WORLD_COLS = 90
DENSITY = 0.3
MAX_ROOM_SIZE = 10
MIN_ROOM_SIZE = 3

VIEW_ROWS = 7
VIEW_COLS = 11

BASE_CELL_SIZE = 128
WALL_SCALE = 1

MOVE_DELAY = 80
FPS = 60

BLACK = (0, 0, 0)
LIGHT_GRAY = (100, 100, 100)
DARK_GRAY = (55, 55, 55)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

# ======================
# INITIALIZE
# ======================

pygame.init()
SCREEN_WIDTH = VIEW_COLS * BASE_CELL_SIZE
SCREEN_HEIGHT = VIEW_ROWS * BASE_CELL_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cave Explorer")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ======================
# GAME STATE
# ======================

cave, (player_x, player_y) = generate_cave(WORLD_ROWS, WORLD_COLS,DENSITY, MIN_ROOM_SIZE)
for rows in cave:
    print(rows)
player_radius = BASE_CELL_SIZE // 4
last_move_time = 0
show_map = False

# ======================
# LIGHT STATE
# ======================

MAX_LIGHT = 100
MIN_LIGHT = 0  # fully dark if desired
light_percentage = MAX_LIGHT
LIGHT_DRAIN_PER_SEC = 0.5  # faster for visible shrinking

# ======================
# HELPERS
# ======================

def can_move(x, y):
    return (
        0 <= x < WORLD_COLS and
        0 <= y < WORLD_ROWS and
        cave[y][x] != 1
    )

def get_camera_offset():
    cam_x = player_x - VIEW_COLS // 2
    cam_y = player_y - VIEW_ROWS // 2

    cam_x = max(0, min(cam_x, WORLD_COLS - VIEW_COLS))
    cam_y = max(0, min(cam_y, WORLD_ROWS - VIEW_ROWS))

    return cam_x, cam_y

def draw_map_button():
    button_rect = pygame.Rect(
        SCREEN_WIDTH - 110,
        10,
        100,
        40
    )
    pygame.draw.rect(screen, (80, 80, 80), button_rect)
    pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)

    text = font.render("MAP (M)", True, (255, 255, 255))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    return button_rect

# ======================
# RENDERING
# ======================

def draw_world():
    cam_x, cam_y = get_camera_offset()

    for row in range(VIEW_ROWS):
        for col in range(VIEW_COLS):
            world_x = cam_x + col
            world_y = cam_y + row

            screen_x = col * BASE_CELL_SIZE
            screen_y = row * BASE_CELL_SIZE

            if not (0 <= world_x < WORLD_COLS and 0 <= world_y < WORLD_ROWS):
                continue

            cell = cave[world_y][world_x]

            if cell == 1:
                size = int(BASE_CELL_SIZE * WALL_SCALE)
                offset = (BASE_CELL_SIZE - size) // 2
                rect = pygame.Rect(
                    screen_x + offset,
                    screen_y + offset,
                    size,
                    size
                )
                pygame.draw.rect(screen, DARK_GRAY, rect)

            else:
                rect = pygame.Rect(
                    screen_x,
                    screen_y,
                    BASE_CELL_SIZE,
                    BASE_CELL_SIZE
                )
                pygame.draw.rect(screen, LIGHT_GRAY, rect)

            if cell == 2:
                pygame.draw.circle(
                    screen,
                    GREEN,
                    (screen_x + BASE_CELL_SIZE // 2,
                     screen_y + BASE_CELL_SIZE // 2),
                    BASE_CELL_SIZE // 6
                )

    # Player (centered)
    pygame.draw.circle(
        screen,
        RED,
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        player_radius
    )

# ------------------
# LIGHT RENDERING
# ------------------

def draw_light_overlay():
    # Create dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))

    # Max radius = screen height / 2
    max_radius = SCREEN_HEIGHT // 2
    radius = int(max_radius * (light_percentage / 100))

    pygame.draw.circle(
        overlay,
        (0, 0, 0, 0),  # transparent
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        radius
    )

    screen.blit(overlay, (0, 0))

def draw_light_ui():
    bar_width = 200
    bar_height = 20
    x = 10
    y = SCREEN_HEIGHT - 40

    # Background
    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, bar_width, bar_height), 2)

    # Fill
    fill_width = int(bar_width * (light_percentage / 100))
    pygame.draw.rect(screen, (240, 240, 100), (x, y, fill_width, bar_height))

    # Text
    text = font.render(f"Light: {int(light_percentage)}%", True, (255, 255, 255))
    screen.blit(text, (x, y - 20))

# ======================
# MAIN LOOP
# ======================

running = True
while running:
    dt = clock.get_time() / 1000  # seconds since last frame
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                show_map = not show_map

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if map_button.collidepoint(event.pos):
                    show_map = not show_map

    # ------------------
    # MOVEMENT
    # ------------------
    if not show_map and current_time - last_move_time >= MOVE_DELAY:
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1

        nx = player_x + dx
        ny = player_y + dy

        if can_move(nx, ny):
            player_x, player_y = nx, ny
            last_move_time = current_time

    # ------------------
    # LIGHT DRAIN
    # ------------------
    if not show_map:
        light_percentage -= LIGHT_DRAIN_PER_SEC * dt
        light_percentage = max(MIN_LIGHT, light_percentage)

    # ------------------
    # DRAW
    # ------------------
    screen.fill(BLACK)

    if show_map:
        draw_map(
            screen,
            cave,
            (player_x, player_y),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
    else:
        draw_world()
        draw_light_overlay()  # light circle shrinks with time
        draw_light_ui()       # light percentage bar

    map_button = draw_map_button()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
