import pygame

# Tile constants
WALL = 1
FLOOR = 0
EXIT = 2
MAP = 3
FOOD = 4
LIGHT = 5
GATE_CLOSED = 6
GATE_OPEN = 7

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

    # Draw map cells
    for y in range(rows):
        for x in range(cols):
            cell = cave[y][x]

            # Wall or floor
            color = (30, 30, 30)  # wall
            if cell == FLOOR:
                color = (120, 120, 120)
            elif cell == WALL:
                color = (60,35,20)
            elif cell == EXIT:
                color = (0, 200, 0)  # exit
            elif cell == GATE_CLOSED:
                color = (0,0,0)
            elif cell == GATE_OPEN:
                color = (255,255,255)

            rect = pygame.Rect(
                offset_x + x * cell_size,
                offset_y + y * cell_size,
                cell_size,
                cell_size
            )
            pygame.draw.rect(screen, color, rect)

            # Draw items as small circles
            circle_radius = cell_size // 3
            circle_center = (
                offset_x + x * cell_size + cell_size // 2,
                offset_y + y * cell_size + cell_size // 2
            )

        

            if cell == MAP:
                pygame.draw.circle(screen, (0, 150, 255), circle_center, circle_radius)
            elif cell == FOOD:
                pygame.draw.circle(screen, (255, 100, 0), circle_center, circle_radius)
            elif cell == LIGHT:
                pygame.draw.circle(screen, (255, 255, 50), circle_center, circle_radius)

    # Draw player as a square (like before)
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

    # Draw legend
    legend_x = offset_x + cols * cell_size + 20
    legend_y = offset_y
    draw_map_legend(screen, legend_x, legend_y)



def draw_map_legend(screen, start_x, start_y):
    font = pygame.font.SysFont(None, 22)
    spacing = 26

    legend_items = [
        ("Wall", (60, 35, 20)),
        ("Floor", (120, 120, 120)),
        ("Exit", (0, 200, 0)),
        ("Closed Gate", (0, 0, 0)),
        ("Open Gate", (255, 255, 255)),
        ("Map", (0, 150, 255)),
        ("Food", (255, 100, 0)),
        ("Light", (255, 255, 50)),
        ("Player", (220, 60, 60)),
    ]

    for i, (label, color) in enumerate(legend_items):
        y = start_y + i * spacing

        # color box
        pygame.draw.rect(screen, color, (start_x, y, 18, 18))
        pygame.draw.rect(screen, (200, 200, 200), (start_x, y, 18, 18), 1)

        # text
        text = font.render(label, True, (220, 220, 220))
        screen.blit(text, (start_x + 26, y - 2))
