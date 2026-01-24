import pygame
from cave import generate_maze

# -------------------
# Config
# -------------------
CELL_SIZE = 32
VIEW_COLS = 11
VIEW_ROWS = 11

SCREEN_WIDTH = VIEW_COLS * CELL_SIZE
SCREEN_HEIGHT = VIEW_ROWS * CELL_SIZE

ROWS = 
COLS = 41

FPS = 60

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 200, 0)
RED = (200, 50, 50)

# -------------------
# Init pygame
# -------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Scrolling Cave")
clock = pygame.time.Clock()

# -------------------
# Maze & player
# -------------------
maze = generate_maze(ROWS, COLS)

player_x, player_y = 0, 0  # start
player_radius = CELL_SIZE // 3

# -------------------
# Helpers
# -------------------
def can_move(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS and maze[y][x] != 1

def get_camera_offset():
    cam_x = player_x - VIEW_COLS // 2
    cam_y = player_y - VIEW_ROWS // 2
    return cam_x, cam_y

def draw_world():
    cam_x, cam_y = get_camera_offset()

    for row in range(VIEW_ROWS):
        for col in range(VIEW_COLS):
            world_x = cam_x + col
            world_y = cam_y + row

            rect = pygame.Rect(
                col * CELL_SIZE,
                row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            if not (0 <= world_x < COLS and 0 <= world_y < ROWS):
                pygame.draw.rect(screen, BLACK, rect)
                continue

            cell = maze[world_y][world_x]

            if cell == 1:
                pygame.draw.rect(screen, DARK_GRAY, rect)
            else:
                pygame.draw.rect(screen, BLACK, rect)

            if cell == 2:
                pygame.draw.circle(screen, GREEN, rect.center, CELL_SIZE // 4)

    # Draw player (always centered)
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2
    pygame.draw.circle(screen, RED, (center_x, center_y), player_radius)

# -------------------
# Main loop
# -------------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    screen.fill(BLACK)
    draw_world()
    pygame.display.flip()

pygame.quit()
