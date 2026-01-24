import pygame
from cave import generate_maze

# -------------------
# Configuration
# -------------------
ROWS = 21
COLS = 21
CELL_SIZE = 32

WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE

FPS = 60

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
GREEN = (0, 200, 0)

# -------------------
# Initialize pygame
# -------------------
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Cave Maze")
clock = pygame.time.Clock()

# -------------------
# Generate maze
# -------------------
maze = generate_maze(ROWS, COLS)
for rows in maze:
    print(rows)

# -------------------
# Draw maze
# -------------------
def draw_maze():
    for y in range(ROWS):
        for x in range(COLS):
            cell = maze[y][x]
            rect = pygame.Rect(
                x * CELL_SIZE,
                y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            )

            if cell == 1:
                # Wall
                pygame.draw.rect(screen, DARK_GRAY, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)  # outline
            elif cell == 0:
                # Empty space
                pygame.draw.rect(screen, BLACK, rect)
            elif cell == 2:
                # End
                pygame.draw.rect(screen, BLACK, rect)
                pygame.draw.circle(
                    screen,
                    GREEN,
                    rect.center,
                    CELL_SIZE // 4
                )

# -------------------
# Main loop
# -------------------
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    draw_maze()
    pygame.display.flip()

pygame.quit()
