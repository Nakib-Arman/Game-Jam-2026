import pygame

# Tile constants
WALL = 1
FLOOR = 0
EXIT = 2
MAP = 3
FOOD = 4
LIGHT = 5

def draw_map(screen, cave, player_pos, screen_size):
    rows = len(cave)
    cols = len(cave[0])

    map_margin = 40
    map_width = screen_size[0] - map_margin * 2
    map_height = screen_size[1] - map_margin * 2

    cell_w = map_width // cols
    cell_h = map_height // rows
    cell_size = min(cell_w, cell_h)

    offset_x = (screen_size[0] - (cols * cell_size)) // 2
    offset_y = (screen_size[1] - (rows * cell_size)) // 2

    for y in range(rows):
        for x in range(cols):
            cell = cave[y][x]

            # Default wall color
            color = (30, 30, 30)
            if cell == FLOOR:
                color = (120, 120, 120)
            elif cell == EXIT:
                color = (0, 200, 0)
            elif cell == MAP:
                color = (0, 150, 255)   # Blue for maps
            elif cell == FOOD:
                color = (255, 180, 0)   # Orange for food
            elif cell == LIGHT:
                color = (255, 255, 100) # Yellow for light

            rect = pygame.Rect(
                offset_x + x * cell_size,
                offset_y + y * cell_size,
                cell_size,
                cell_size
            )
            pygame.draw.rect(screen, color, rect)

    # Draw player
    px, py = player_pos
    player_rect = pygame.Rect(
        offset_x + px * cell_size,
        offset_y + py * cell_size,
        cell_size,
        cell_size
    )
    pygame.draw.rect(screen, (220, 60, 60), player_rect)

    # Border around the map
    pygame.draw.rect(
        screen,
        (200, 200, 200),
        (
            offset_x,
            offset_y,
            cols * cell_size,
            rows * cell_size
        ),
        2
    )
