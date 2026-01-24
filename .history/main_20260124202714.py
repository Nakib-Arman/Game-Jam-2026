import pygame
from cave import generate_maze

# ======================
# CONFIGURATION
# ======================

# World size (maze)
WORLD_ROWS = 41
WORLD_COLS = 41

# Viewport (how much is rendered)
VIEW_ROWS = 7
VIEW_COLS = 7

# Cell sizes
BASE_CELL_SIZE = 128          # overall scale
PATH_SCALE = 1            # 0 cells
WALL_SCALE = 0.5             # 1 cells (smaller)

# Movement
MOVE_DELAY = 80              # milliseconds (higher = slower)

# FPS
FPS = 60

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (55, 55, 55)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

# ======================
# INITIALIZE PYGAME
# ======================

pygame.init()
SCREEN_WIDTH = VIEW_COLS * BASE_CELL_SIZE
SCREEN_HEIGHT = VIEW_ROWS * BASE_CELL_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cave Explorer")
clock = pygame.time.Clock()

# ======================
# GAME STATE
# ======================

maze = generate_maze(WORLD_ROWS, WORLD_COLS)

player_x, player_y = 0, 0
player_radius = BASE_CELL_SIZE // 4

last_move_time = 0  # for movement cooldown

# ======================
# HELPERS
# ======================

def can_move(x, y):
    return (
        0 <= x < WORLD_COLS and
        0 <= y < WORLD_ROWS and
        maze[y][x] != 1
    )

def get_camera_offset():
    cam_x = player_x - VIEW_COLS // 2
    cam_y = player_y - VIEW_ROWS // 2
    return cam_x, cam_y

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

            cell = maze[world_y][world_x]

            if cell == 1:
                size = int(BASE_CELL_SIZE * WALL_SCALE)
                offset = (BASE_CELL_SIZE - size) // 2
                rect1 = pygame.Rect(
                    screen_x,
                    screen_y,
                    size,
                    size
                )

                pygame.draw.rect(screen, DARK_GRAY, rect)
                pygame.draw.rect(screen, DARK_GRAY, rect2)

            else:
                size = int(BASE_CELL_SIZE * PATH_SCALE)
                rect = pygame.Rect(
                    screen_x,
                    screen_y,
                    size,
                    size
                )
                pygame.draw.rect(screen, BLACK, rect)

            if cell == 2:
                pygame.draw.circle(
                    screen,
                    GREEN,
                    (screen_x + BASE_CELL_SIZE // 2,
                     screen_y + BASE_CELL_SIZE // 2),
                    BASE_CELL_SIZE // 6
                )

    # Player (always centered)
    pygame.draw.circle(
        screen,
        RED,
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
        player_radius
    )

# ======================
# MAIN LOOP
# ======================

running = True
while running:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ------------------
    # MOVEMENT (SLOWED)
    # ------------------
    if current_time - last_move_time >= MOVE_DELAY:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1

        new_x = player_x + dx
        new_y = player_y + dy

        if can_move(new_x, new_y):
            player_x, player_y = new_x, new_y
            last_move_time = current_time

    # ------------------
    # DRAW
    # ------------------
    screen.fill(BLACK)
    draw_world()
    pygame.display.flip()

pygame.quit()
