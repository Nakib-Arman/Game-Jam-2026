import pygame
from cave import generate_cave
from map import draw_map

# ======================
# CONFIGURATION
# ======================

LEVEL = "hard"

if LEVEL == "easy":
    WORLD_ROWS = 46
    WORLD_COLS = 50
elif LEVEL == "medium":
    WORLD_ROWS = 71
    WORLD_COLS = 75
elif LEVEL == "hard":
    WORLD_ROWS = 96
    WORLD_COLS = 100

DENSITY = 0.2
MAX_ROOM_SIZE = 10
MIN_ROOM_SIZE = 3

VIEW_ROWS = 7
VIEW_COLS = 11

BASE_CELL_SIZE = 128
WALL_SCALE = 1

FPS = 60

BLACK = (0, 0, 0)
LIGHT_GRAY = (100, 100, 100)
DARK_GRAY = (55, 55, 55)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

# ======================
# MOVEMENT SETTINGS
# ======================

MAX_MOVE_SPEED = 200  # pixels/sec when energy is full
MIN_MOVE_SPEED = 0    # pixels/sec when energy is empty

# ======================
# LIGHT SETTINGS
# ======================

MAX_LIGHT = 100
MIN_LIGHT = 0
LIGHT_DRAIN_PER_SEC = 0.85

# ======================
# ENERGY SETTINGS
# ======================

MAX_ENERGY = 100
MIN_ENERGY = 0
ENERGY_DRAIN_PER_SEC = 0.6

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

cave, (player_cell_x, player_cell_y) = generate_cave(
    WORLD_ROWS, WORLD_COLS, DENSITY, MIN_ROOM_SIZE, MAX_ROOM_SIZE
)

# Pixel coordinates
player_x = player_cell_x * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
player_y = player_cell_y * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
player_radius = BASE_CELL_SIZE // 4

show_map = False
light_percentage = MAX_LIGHT
energy_percentage = MAX_ENERGY

# ======================
# HELPERS
# ======================

def can_move_pixel(x, y):
    """Check if the player (circle) at pixel (x, y) collides with walls."""
    left = x - player_radius
    right = x + player_radius
    top = y - player_radius
    bottom = y + player_radius

    cells_to_check = set()
    cells_to_check.add((int(left // BASE_CELL_SIZE), int(top // BASE_CELL_SIZE)))
    cells_to_check.add((int(right // BASE_CELL_SIZE), int(top // BASE_CELL_SIZE)))
    cells_to_check.add((int(left // BASE_CELL_SIZE), int(bottom // BASE_CELL_SIZE)))
    cells_to_check.add((int(right // BASE_CELL_SIZE), int(bottom // BASE_CELL_SIZE)))

    for cell_x, cell_y in cells_to_check:
        if 0 <= cell_x < WORLD_COLS and 0 <= cell_y < WORLD_ROWS:
            if cave[cell_y][cell_x] == 1:
                return False
        else:
            return False
    return True

def get_camera_offset():
    cam_x = player_x - SCREEN_WIDTH // 2
    cam_y = player_y - SCREEN_HEIGHT // 2

    max_cam_x = WORLD_COLS * BASE_CELL_SIZE - SCREEN_WIDTH
    max_cam_y = WORLD_ROWS * BASE_CELL_SIZE - SCREEN_HEIGHT

    cam_x = max(0, min(cam_x, max_cam_x))
    cam_y = max(0, min(cam_y, max_cam_y))

    return int(cam_x), int(cam_y)

def draw_map_button():
    button_rect = pygame.Rect(SCREEN_WIDTH - 110, 10, 100, 40)
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
            world_x = col + cam_x // BASE_CELL_SIZE
            world_y = row + cam_y // BASE_CELL_SIZE

            screen_x = col * BASE_CELL_SIZE - (cam_x % BASE_CELL_SIZE)
            screen_y = row * BASE_CELL_SIZE - (cam_y % BASE_CELL_SIZE)

            if not (0 <= world_x < WORLD_COLS and 0 <= world_y < WORLD_ROWS):
                continue

            cell = cave[world_y][world_x]

            if cell == 1:
                size = int(BASE_CELL_SIZE * WALL_SCALE)
                offset = (BASE_CELL_SIZE - size) // 2
                rect = pygame.Rect(screen_x + offset, screen_y + offset, size, size)
                pygame.draw.rect(screen, DARK_GRAY, rect)
            else:
                rect = pygame.Rect(screen_x, screen_y, BASE_CELL_SIZE, BASE_CELL_SIZE)
                pygame.draw.rect(screen, LIGHT_GRAY, rect)

            if cell == 2:
                pygame.draw.circle(
                    screen,
                    GREEN,
                    (screen_x + BASE_CELL_SIZE // 2, screen_y + BASE_CELL_SIZE // 2),
                    BASE_CELL_SIZE // 6,
                )

    # Player
    screen_center_x = player_x - cam_x
    screen_center_y = player_y - cam_y
    pygame.draw.circle(screen, RED, (int(screen_center_x), int(screen_center_y)), player_radius)

# ------------------
# LIGHT RENDERING
# ------------------

def draw_light_overlay():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))

    max_radius = SCREEN_HEIGHT // 2
    radius = int(max_radius * (light_percentage / 100))
    center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    fade_width = max(1, int(radius * 0.35))

    for r in range(radius, 0, -1):
        t = r / radius
        alpha = int(230 * t * t)
        pygame.draw.circle(overlay, (0, 0, 0, alpha), center, r)

    screen.blit(overlay, (0, 0))

def draw_light_ui():
    bar_width = 200
    bar_height = 20
    x, y = 10, SCREEN_HEIGHT - 40

    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, bar_width, bar_height), 2)

    fill_width = int(bar_width * (light_percentage / 100))
    pygame.draw.rect(screen, (240, 240, 100), (x, y, fill_width, bar_height))
    text = font.render(f"Light: {int(light_percentage)}%", True, (255, 255, 255))
    screen.blit(text, (x + 210, y + 5))

def draw_energy_ui():
    bar_width = 200
    bar_height = 20
    x, y = 10, SCREEN_HEIGHT - 70

    pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, bar_width, bar_height), 2)

    fill_width = int(bar_width * (energy_percentage / 100))
    pygame.draw.rect(screen, (100, 200, 255), (x, y, fill_width, bar_height))
    text = font.render(f"Energy: {int(energy_percentage)}%", True, (255, 255, 255))
    screen.blit(text, (x + 210, y + 5))

# ======================
# MAIN LOOP
# ======================

running = True
while running:
    dt = clock.tick(FPS) / 1000  # seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            show_map = not show_map
            

    # ------------------
    # PIXEL MOVEMENT
    # ------------------
    if not show_map:
        keys = pygame.key.get_pressed()

        # speed scales with energy
        current_speed = MIN_MOVE_SPEED + (MAX_MOVE_SPEED - MIN_MOVE_SPEED) * (energy_percentage / 100)

        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -current_speed * dt
        if keys[pygame.K_RIGHT]:
            dx = current_speed * dt
        if keys[pygame.K_UP]:
            dy = -current_speed * dt
        if keys[pygame.K_DOWN]:
            dy = current_speed * dt

        # Move horizontally
        if can_move_pixel(player_x + dx, player_y):
            player_x += dx
        # Move vertically
        if can_move_pixel(player_x, player_y + dy):
            player_y += dy

        # Light & energy drain
        light_percentage = max(MIN_LIGHT, light_percentage - LIGHT_DRAIN_PER_SEC * dt)
        energy_percentage = max(MIN_ENERGY, energy_percentage - ENERGY_DRAIN_PER_SEC * dt)

    # ------------------
    # DRAW
    # ------------------
    screen.fill(BLACK)

    if show_map:
        draw_map(screen, cave, (int(player_x // BASE_CELL_SIZE), int(player_y // BASE_CELL_SIZE)),
                 (SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        draw_world()
        draw_light_overlay()
        draw_light_ui()
        draw_energy_ui()

    map_button = draw_map_button()
    pygame.display.flip()

pygame.quit()
