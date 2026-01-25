import random
from collections import deque

WALL = 1
FLOOR = 0
EXIT = 2


def generate_cave(rows, cols,
                  room_attempts=40,  # increased to add more rooms
                  min_room_size=3,
                  max_room_size=6):

    cave = [[WALL for _ in range(cols)] for _ in range(rows)]

    # ----------------------
    # Maze generation (DFS)
    # ----------------------
    def carve_maze(x, y):
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 1 <= nx < cols - 1 and 1 <= ny < rows - 1:
                if cave[ny][nx] == WALL:
                    cave[y + dy // 2][x + dx // 2] = FLOOR
                    cave[ny][nx] = FLOOR
                    carve_maze(nx, ny)

    start_x, start_y = 1, 1
    cave[start_y][start_x] = FLOOR
    carve_maze(start_x, start_y)

    # ----------------------
    # Helper functions for rooms
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
    # Carve more rooms
    # ----------------------
    for _ in range(room_attempts):
        w = random.randint(min_room_size, max_room_size)
        h = random.randint(min_room_size, max_room_size)
        x = random.randint(1, cols - w - 2)
        y = random.randint(1, rows - h - 2)

        new_room = (x, y, w, h)
        # allow rooms to overlap maze corridors slightly
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




