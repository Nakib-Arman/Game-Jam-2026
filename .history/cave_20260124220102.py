import random
from collections import deque

WALL = 1
FLOOR = 0
EXIT = 2


def generate_cave(rows, cols):

    cave = [[WALL for _ in range(cols)] for _ in range(rows)]

    # --------------------------------------------------
    # BASIC HELPERS
    # --------------------------------------------------
    def carve(x, y):
        if 0 <= x < cols and 0 <= y < rows:
            cave[y][x] = FLOOR

    def carve_block(cx, cy, r):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                carve(x, y)

    # --------------------------------------------------
    # 1️⃣ BACKBONE PATH (TWISTY, SHORT SEGMENTS)
    # --------------------------------------------------
    x, y = random.randint(2, cols - 3), random.randint(2, rows - 3)
    spawn = (x, y)

    path = [(x, y)]
    direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    for _ in range(rows * 3):
        carve(x, y)

        # short segments only
        if random.random() < 0.7:
            direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

        dx, dy = direction
        nx, ny = x + dx, y + dy

        if 1 < nx < cols - 2 and 1 < ny < rows - 2:
            x, y = nx, ny
            path.append((x, y))

    # --------------------------------------------------
    # 2️⃣ EXPAND BACKBONE INTO ROOMS (BIG + SMALL)
    # --------------------------------------------------
    for (x, y) in path:
        roll = random.random()
        if roll < 0.10:
            carve_block(x, y, 3)   # big chamber
        elif roll < 0.35:
            carve_block(x, y, 2)   # medium room
        elif roll < 0.70:
            carve_block(x, y, 1)   # small widening
        else:
            carve(x, y)            # narrow path

    # --------------------------------------------------
    # 3️⃣ SHORT SIDE PASSAGES (CONNECTED ONLY)
    # --------------------------------------------------
    for (sx, sy) in random.sample(path, len(path)//3):
        x, y = sx, sy
        direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

        length = random.randint(3, 7)  # short passages
        for _ in range(length):
            carve(x, y)
            if random.random() < 0.6:
                direction = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            dx, dy = direction
            nx, ny = x + dx, y + dy
            if 1 < nx < cols - 2 and 1 < ny < rows - 2:
                x, y = nx, ny

    # --------------------------------------------------
    # 4️⃣ LOOP CONNECTIONS (COMPLEXITY)
    # --------------------------------------------------
    for _ in range(len(path)//4):
        x, y = random.choice(path)
        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        for _ in range(random.randint(2, 4)):
            carve(x, y)
            x += dx
            y += dy

    # --------------------------------------------------
    # 5️⃣ FIND EXIT (FARTHEST BY GRAPH DISTANCE)
    # --------------------------------------------------
    exit_x, exit_y = find_farthest_cell(cave, spawn[0], spawn[1])
    cave[exit_y][exit_x] = EXIT

    return cave, spawn


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
