import pygame
from cave import generate_maze

# ======================
# CONFIGURATION
# ======================

WORLD_ROWS = 41
WORLD_COLS = 41

VIEW_ROWS = 7
VIEW_COLS = 11

# Tile sizes
ROAD_SIZE = 128
WALL_SIZE = 64   # half of road → road is twice as big

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

SCREEN_WIDTH = VIEW_COLS * ROAD_SIZE
SCREEN_HEIGHT = VIEW_ROWS * ROAD_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cave Explorer")
clock = pygame.time.Clock()

# ======================
# GAME STATE
# ======================

maze = generate_maze(WORLD_ROWS, WORLD_COLS)

player_x, player_y = 0, 0
player_radius = ROAD_SIZE // 4
last_move_time = 0

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
    return (
        player_x - VIEW_COLS // 2,
        player_y - VIEW_ROWS // 2
    )

# ======================
# RENDERING
# ======================

def draw_world():
    cam_x, cam_y = get_camera_offset()

    for row in range(VIEW_ROWS):
        for col in range(VIEW_COLS):
            world_x = cam_x + col
            world_y = cam_y + row

            if not (0 <= world_x < WORLD_COLS and 0 <= world_y < WORLD_ROWS):
                continue

            cell = maze[world_y][world_x]

            # Screen anchor always based on ROAD_SIZE grid
            screen_x = col * ROAD_SIZE
            screen_y = row * ROAD_SIZE

            # Decide size based on cell type
            if cell == 1:  # WALL
                size = WALL_SIZE
                color = DARK_GRAY
                offset = (ROAD_SIZE - WALL_SIZE) // 2
            else:          # ROAD or GOAL
                size = ROAD_SIZE
                color = LIGHT_GRAY
                offset = 0

            rect = pygame.Rect(
                screen_x + offset,
                screen_y + offset,
                size,
                size
            )
            pygame.draw.rect(screen, color, rect)

            if cell == 2:
                pygame.draw.circle(
                    screen,
                    GREEN,
                    (screen_x + ROAD_SIZE // 2,
                     screen_y + ROAD_SIZE // 2),
                    ROAD_SIZE // 6
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

    if current_time - last_move_time >= MOVE_DELAY:
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

        nx, ny = player_x + dx, player_y + dy
        if can_move(nx, ny):
            player_x, player_y = nx, ny
            last_move_time = current_time

    screen.fill(BLACK)
    draw_world()
    pygame.display.flip()

pygame.quit()
