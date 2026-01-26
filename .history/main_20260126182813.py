import pygame
from cave import generate_cave
from map import draw_map

# ======================
# CONFIGURATION
# ======================

LEVEL = "easy"

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
LIGHT_GRAY = (98, 87, 85)
GREEN = (0, 200, 0)

# ======================
# MOVEMENT SETTINGS
# ======================

MAX_MOVE_SPEED = 500
MIN_MOVE_SPEED = 0

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
screen = pygame.display.set_mode(
    (VIEW_COLS * BASE_CELL_SIZE, VIEW_ROWS * BASE_CELL_SIZE)
)
pygame.display.set_caption("Cave Explorer")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 26)

SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

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
FRAMES_PER_ANIMATION = 4

def extract_frames(sheet, row):
    frames = []
    for col in range(FRAMES_PER_ANIMATION):
        frame = sheet.subsurface(
            pygame.Rect(
                col * SPRITE_WIDTH,
                row * SPRITE_HEIGHT,
                SPRITE_WIDTH,
                SPRITE_HEIGHT,
            )
        )
        frame = pygame.transform.scale(
            frame, (BASE_CELL_SIZE // 2, BASE_CELL_SIZE // 2)
        )
        frames.append(frame)
    return frames

sprites = {
    "down": extract_frames(character_sheet, 0),
    "left": extract_frames(character_sheet, 1),
    "right": extract_frames(character_sheet, 2),
    "up": extract_frames(character_sheet, 3),
}

# ======================
# GAME STATE
# ======================

GAME_STATE = "MENU"  # MENU | PLAYING

cave = None
player_x = player_y = 0
player_radius = BASE_CELL_SIZE // 4

light_percentage = MAX_LIGHT
energy_percentage = MAX_ENERGY

player_direction = "down"
animation_frame = 0
animation_timer = 0
ANIMATION_SPEED = 0.15

show_map = False

# ======================
# HELPERS
# ======================

def can_move_pixel(x, y):
    left = x - player_radius
    right = x + player_radius
    top = y - player_radius
    bottom = y + player_radius

    cells = {
        (int(left // BASE_CELL_SIZE), int(top // BASE_CELL_SIZE)),
        (int(right // BASE_CELL_SIZE), int(top // BASE_CELL_SIZE)),
        (int(left // BASE_CELL_SIZE), int(bottom // BASE_CELL_SIZE)),
        (int(right // BASE_CELL_SIZE), int(bottom // BASE_CELL_SIZE)),
    }

    for cx, cy in cells:
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

def draw_button(rect, text, hover):
    color = (120, 120, 120) if hover else (80, 80, 80)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (200, 200, 200), rect, 2)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=rect.center))

# ======================
# MENU
# ======================

def draw_menu(mouse_pos):
    screen.fill((20, 20, 20))
    title_font = pygame.font.SysFont(None, 64)
    title = title_font.render("CAVE EXPLORER", True, (240, 240, 240))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 120)))

    buttons = {}
    w, h = 260, 60
    y = 260
    gap = 80

    buttons["new"] = pygame.Rect(SCREEN_WIDTH//2-w//2, y, w, h)
    buttons["continue"] = pygame.Rect(SCREEN_WIDTH//2-w//2, y+gap, w, h)
    buttons["quit"] = pygame.Rect(SCREEN_WIDTH//2-w//2, y+gap*2, w, h)

    for k, r in buttons.items():
        draw_button(r, k.upper(), r.collidepoint(mouse_pos))

    return buttons

def start_new_game():
    global cave, player_x, player_y
    global light_percentage, energy_percentage
    global GAME_STATE

    cave, (cx, cy) = generate_cave(
        WORLD_ROWS, WORLD_COLS, DENSITY, MIN_ROOM_SIZE, MAX_ROOM_SIZE
    )

    player_x = cx * BASE_CELL_SIZE + BASE_CELL_SIZE // 2
    player_y = cy * BASE_CELL_SIZE + BASE_CELL_SIZE // 2

    light_percentage = MAX_LIGHT
    energy_percentage = MAX_ENERGY

    GAME_STATE = "PLAYING"

# ======================
# RENDER WORLD
# ======================

def draw_world():
    cam_x, cam_y = get_camera_offset()

    for row in range(VIEW_ROWS):
        for col in range(VIEW_COLS):
            wx = col + cam_x // BASE_CELL_SIZE
            wy = row + cam_y // BASE_CELL_SIZE

            sx = col * BASE_CELL_SIZE - cam_x % BASE_CELL_SIZE
            sy = row * BASE_CELL_SIZE - cam_y % BASE_CELL_SIZE

            if not (0 <= wx < WORLD_COLS and 0 <= wy < WORLD_ROWS):
                continue

            if cave[wy][wx] == 1:
                screen.blit(wall_image, (sx, sy))
            else:
                pygame.draw.rect(
                    screen, LIGHT_GRAY,
                    (sx, sy, BASE_CELL_SIZE, BASE_CELL_SIZE)
                )

    sprite = sprites[player_direction][animation_frame]
    screen.blit(
        sprite,
        sprite.get_rect(center=(player_x-cam_x, player_y-cam_y))
    )

def draw_light_overlay():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))

    radius = int((SCREEN_HEIGHT // 2) * (light_percentage / 100))
    center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    for r in range(radius, 0, -1):
        alpha = int(230 * (r / radius) ** 2)
        pygame.draw.circle(overlay, (0, 0, 0, alpha), center, r)

    screen.blit(overlay, (0, 0))

# ======================
# MAIN LOOP
# ======================

running = True
while running:
    dt = clock.tick(FPS) / 1000
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if GAME_STATE == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons["new"].collidepoint(event.pos):
                    start_new_game()
                elif buttons["quit"].collidepoint(event.pos):
                    running = False

    if GAME_STATE == "MENU":
        buttons = draw_menu(mouse_pos)

    elif GAME_STATE == "PLAYING":
        keys = pygame.key.get_pressed()
        speed = MIN_MOVE_SPEED + (MAX_MOVE_SPEED - MIN_MOVE_SPEED) * (energy_percentage / 100)

        dx = dy = 0
        moving = False

        if keys[pygame.K_LEFT]:
            dx = -speed * dt
            player_direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT]:
            dx = speed * dt
            player_direction = "right"
            moving = True
        elif keys[pygame.K_UP]:
            dy = -speed * dt
            player_direction = "up"
            moving = True
        elif keys[pygame.K_DOWN]:
            dy = speed * dt
            player_direction = "down"
            moving = True

        if can_move_pixel(player_x + dx, player_y):
            player_x += dx
        if can_move_pixel(player_x, player_y + dy):
            player_y += dy

        if moving:
            animation_timer += dt
            if animation_timer >= ANIMATION_SPEED:
                animation_timer = 0
                animation_frame = (animation_frame + 1) % 4
        else:
            animation_frame = 0

        light_percentage = max(MIN_LIGHT, light_percentage - LIGHT_DRAIN_PER_SEC * dt)
        energy_percentage = max(MIN_ENERGY, energy_percentage - ENERGY_DRAIN_PER_SEC * dt)

        screen.fill(BLACK)
        draw_world()
        draw_light_overlay()

    pygame.display.flip()

pygame.quit()
