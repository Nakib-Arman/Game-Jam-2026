import random
from collections import deque

WALL = 1
FLOOR = 0
EXIT = 2

def generate_cave(rows, cols,
                  room_attempts=40,
                  min_room_size=5,
                  max_room_size=10):

    cave = [[WALL for _ in range(cols)] for _ in range(rows)]
    rooms = []

    # -----------------------------
    # Room helpers
    # -----------------------------
    def carve_room(x, y, w, h):
        for iy in range(y, y + h):
            for ix in range(x, x + w):
                cave[iy][ix] = FLOOR

    def intersects(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (
            x1 + w1 < x2 or
            x2 + w2 < x1 or
            y1 + h1 < y2 or
            y2 + h2 < y1
        )

    # -----------------------------
    # Generate rooms
    # -----------------------------
    for _ in range(room_attempts):
        w = random.randint(min_room_size, max_room_size)
        h = random.randint(min_room_size, max_room_size)
        x = random.randint(1, cols - w - 2)
        y = random.randint(1, rows - h - 2)

        new_room = (x, y, w, h)

        if any(intersects(new_room, r) for r in rooms):
            continue

        carve_room(x, y, w, h)
        rooms.append(new_room)

    if not rooms:
        return cave

    # -----------------------------
    # Connect rooms
    # -----------------------------
    def center(room):
        x, y, w, h = room
        return (x + w // 2, y + h // 2)

    for i in range(1, len(rooms)):
        x1, y1 = center(rooms[i - 1])
        x2, y2 = center(rooms[i])

        if random.choice([True, False]):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                cave[y1][x] = FLOOR
            for y in range(min(y1, y2), max(y1, y2) + 1):
                cave[y][x2] = FLOOR
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                cave[y][x1] = FLOOR
            for x in range(min(x1, x2), max(x1, x2) + 1):
                cave[y2][x] = FLOOR

    # -----------------------------
    # Place exit far away
    # -----------------------------
    sx, sy = center(rooms[0])
    ex, ey = find_farthest_cell(cave, sx, sy)
    cave[ey][ex] = EXIT

    return cave


def find_farthest_cell(cave, start_x, start_y):
    rows, cols = len(cave), len(cave[0])
    dist = [[-1]*cols for _ in range(rows)]
    queue = deque([(start_x, start_y)])
    dist[start_y][start_x] = 0

    farthest = (start_x, start_y)

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0,-1),(1,0),(0,1),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if cave[ny][nx] != WALL and dist[ny][nx] == -1:
                    dist[ny][nx] = dist[y][x] + 1
                    queue.append((nx, ny))
                    farthest = (nx, ny)

    return farthest
