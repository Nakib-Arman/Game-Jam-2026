import random
from collections import deque

WALL = 1
FLOOR = 0
EXIT = 2

TOP_BORDER = 3
BOTTOM_BORDER = 3
LEFT_BORDER = 5
RIGHT_BORDER = 5


def generate_cave(rows, cols,
                  room_attempt,
                  min_room_size=3,
                  max_room_size=6):

    cave = [[WALL for _ in range(cols)] for _ in range(rows)]

    # Compute valid carving area
    min_x = LEFT_BORDER
    max_x = cols - RIGHT_BORDER - 1
    min_y = TOP_BORDER
    max_y = rows - BOTTOM_BORDER - 1

    # ----------------------
    # Maze generation (DFS)
    # ----------------------
    def carve_maze(x, y):
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if min_x <= nx <= max_x and min_y <= ny <= max_y:
                if cave[ny][nx] == WALL:
                    cave[y + dy // 2][x + dx // 2] = FLOOR
                    cave[ny][nx] = FLOOR
                    carve_maze(nx, ny)

    # Start maze safely inside borders
    start_x = min_x | 1   # ensure odd
    start_y = min_y | 1
    cave[start_y][start_x] = FLOOR
    carve_maze(start_x, start_y)

    # ----------------------
    # Room helpers
    # ----------------------
    rooms = []

    def carve_room(x, y, w, h):
        for iy in range(y, y + h):
            for ix in range(x, x + w):
                cave[iy][ix] = FLOOR

    def intersects(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (
            x1 + w1 + 1 < x2 or
            x2 + w2 + 1 < x1 or
            y1 + h1 + 1 < y2 or
            y2 + h2 + 1 < y1
        )

    def center(room):
        x, y, w, h = room
        return (x + w // 2, y + h // 2)

    # ----------------------
    # Carve rooms (inside borders)
    # ----------------------
    for _ in range(room_attempts):
        w = random.randint(min_room_size, max_room_size)
        h = random.randint(min_room_size, max_room_size)

        x = random.randint(min_x, max_x - w)
        y = random.randint(min_y, max_y - h)

        new_room = (x, y, w, h)

        if any(intersects(new_room, r) for r in rooms):
            continue

        carve_room(x, y, w, h)
        rooms.append(new_room)

    # ----------------------
    # Spawn & exit
    # ----------------------
    if rooms:
        spawn_x, spawn_y = center(rooms[0])
    else:
        spawn_x, spawn_y = start_x, start_y

    exit_x, exit_y = find_farthest_cell(cave, spawn_x, spawn_y)
    cave[exit_y][exit_x] = EXIT

    return cave, (spawn_x, spawn_y)


def find_farthest_cell(cave, start_x, start_y):
    rows, cols = len(cave), len(cave[0])
    dist = [[-1] * cols for _ in range(rows)]
    queue = deque([(start_x, start_y)])
    dist[start_y][start_x] = 0
    farthest = (start_x, start_y)

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if cave[ny][nx] != WALL and dist[ny][nx] == -1:
                    dist[ny][nx] = dist[y][x] + 1
                    queue.append((nx, ny))
                    farthest = (nx, ny)

    return farthest
