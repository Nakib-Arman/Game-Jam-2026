# cave_window.py
import pygame
from cave import generate_cave
from map import draw_map

def run_cave():
    pygame.init()

    # ======================
    # CONFIGURATION
    # ======================

    LEVEL = "easy"
    WORLD_ROWS, WORLD_COLS = 46, 50

    BASE_CELL_SIZE = 128
    VIEW_ROWS = 7
    VIEW_COLS = 11
    FPS = 60

    SCREEN_WIDTH = VIEW_COLS * BASE_CELL_SIZE
    SCREEN_HEIGHT = VIEW_ROWS * BASE_CELL_SIZE

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Cave Explorer")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    BLACK = (0, 0, 0)
    LIGHT_GRAY = (98, 87, 85)
    GREEN = (0, 200, 0)

    MAX_MOVE_SPEED = 500
    ENERGY = 100
    LIGHT = 100

    # ======================
    # LOAD ASSETS
    # ======================

    wall_image = pygame.image.load("assets/wall_block.png")
    wall_image = pygame.transform.scale(wall_image, (BASE_CELL_SIZE, BASE_CELL_SIZE))

    cave, (px, py) = generate_cave(WORLD_ROWS, WORLD_COLS, 0.2, 3, 10)

    player_x = px * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    player_y = py * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    player_radius = BASE_CELL_SIZE // 4

    def can_move(x, y):
        cx = int(x // BASE_CELL_SIZE)
        cy = int(y // BASE_CELL_SIZE)
        if 0 <= cx < WORLD_COLS and 0 <= cy < WORLD_ROWS:
            return cave[cy][cx] != 1
        return False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # back to home

        keys = pygame.key.get_pressed()
        speed = MAX_MOVE_SPEED * (ENERGY / 100)

        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -speed * dt
        if keys[pygame.K_RIGHT]:
            dx = speed * dt
        if keys[pygame.K_UP]:
            dy = -speed * dt
        if keys[pygame.K_DOWN]:
            dy = speed * dt

        if can_move(player_x + dx, player_y):
            player_x += dx
        if can_move(player_x, player_y + dy):
            player_y += dy

        ENERGY = max(0, ENERGY - 0.6 * dt)
        LIGHT = max(0, LIGHT - 0.85 * dt)

        screen.fill(BLACK)

        cam_x = int(player_x - SCREEN_WIDTH // 2)
        cam_y = int(player_y - SCREEN_HEIGHT // 2)

        for r in range(VIEW_ROWS):
            for c in range(VIEW_COLS):
                wx = c + cam_x // BASE_CELL_SIZE
                wy = r + cam_y // BASE_CELL_SIZE
                sx = c * BASE_CELL_SIZE
                sy = r * BASE_CELL_SIZE

                if 0 <= wx < WORLD_COLS and 0 <= wy < WORLD_ROWS:
                    if cave[wy][wx] == 1:
                        screen.blit(wall_image, (sx, sy))
                    else:
                        pygame.draw.rect(
                            screen,
                            LIGHT_GRAY,
                            (sx, sy, BASE_CELL_SIZE, BASE_CELL_SIZE),
                        )

        pygame.draw.circle(
            screen,
            (200, 50, 50),
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            player_radius,
        )

        pygame.display.flip()
