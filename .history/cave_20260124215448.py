import random
from collections import deque

WALL = 1
FLOOR = 0
EXIT = 2


def generate_cave(rows, cols):

    cave = [[WALL for _ in range(cols)] for _ in range(rows)]
    rooms = []

    # --------------------------------------------------
    # BASIC HELPERS
    # --------------------------------------------------
    def carve(x, y):
        if 0 <= x < cols and 0 <= y < rows:
            cave[y][x] = FLOOR

    def carve_room(x, y, w, h):
        for iy in range(y, y + h):
            for ix in range(x, x + w):
                carve(ix, iy)

    def intersects(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (
            x1 + w1 < x2 or
            x2 + w2 < x1 or
            y1 + h1 < y2 or
            y2 + h2 < y1
        )

    def center(room):
        x, y, w, h = room
        return (x + w // 2, y + h // 2)

    # --------------------------------------------------
    # 1️⃣ BIG ROOMS (FEWER)
    # --------------------------------------------------
    for _ in range(15):
        w = random.randint(6, 10)
        h = random.randint(6, 10)
        x = random.randint(2, cols - w - 3)
        y = random.randint(2, rows - h - 3)

        new_room = (x, y, w, h)
        if any(intersects(new_room, r) for r in rooms):
            continue

        carve_room(x, y, w, h)
        rooms.append(new_room)

    # --------------------------------------------------
    # 2️⃣ SMALL MICRO ROOMS (LOTS)
    # --------------------------------------------------
    for _ in range(40):
        w = random.randint(2, 4)
        h = random.randint(2, 4)
        x = random.randint(1, cols - w - 2)
        y = random.randint(1, rows - h - 2)

        carve_room(x, y, w, h)

    # --------------------------------------------------
    # 3️⃣ CONNECT ROOMS (MULTIPLE LOOPS)
    # --------------------------------------------------
    for i in range(len(rooms)):
        x1, y1 = center(rooms[i])
        x2, y2 = center(random.choice(rooms))

        for x in range(min(x1, x2), max(x1, x2) + 1):
            carve(x, y1)
        for y in range(min(y1, y2), max(y1, y2) + 1):
            carve(x2, y)

    # --------------------------------------------------
    # 4️⃣ DRUNK WALK TUNNELS (NOISE)
    # --------------------------------------------------
    for _ in range(200):
        x = random.randint(1, cols - 2)
        y = random.randint(1, rows - 2)

        for _ in range(random.randint(10, 30)):
            carve(x, y)
            dx, dy = random.choice([(0,1),(1,0),(0,-1),(-1,0)])
            x = max(1, min(cols - 2, x + dx))
            y = max(1, min(rows - 2, y + dy))

    # --------------------------------------------------
    # 5️⃣ CELLULAR AUTOMATA SMOOTHING
    # --------------------------------------------------
    for _ in range(4):
        new_map = [[cave[y][x] for x in range(cols)] for y in range(rows)]
        for y in range(1, rows - 1):
            for x in range(1, cols - 1):
                walls = 0
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    if cave[y+dy][x+dx] == WALL:
                        walls += 1
                if walls <= 1:
                    new_map[y][x] = FLOOR
        cave = new_map

    # --------------------------------------------------
    # 6️⃣ SPAWN & EXIT
    # --------------------------------------------------
    spawn_x, spawn_y = center(random.choice(rooms))
    exit_x, exit_y = find_farthest_cell(cave, spawn_x, spawn_y)
    cave[exit_y][exit_x] = EXIT

    return cave, (spawn_x, spawn_y)


def find_farthest_cell(cave, sx, sy):
    rows, cols = len(cave), len(cave[0])
    dist = [[-1]*cols for _ in range(rows)]
    q = deque([(sx, sy)])
    dist[sy][sx] = 0

    farthest = (sx, sy)

    while q:
        x, y = q.popleft()
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if cave[ny][nx] != WALL and dist[ny][nx] == -1:
                    dist[ny][nx] = dist[y][x] + 1
                    q.append((nx, ny))
                    farthest = (nx, ny)

    return farthest
