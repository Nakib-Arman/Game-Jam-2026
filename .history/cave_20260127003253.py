import random
from collections import deque
import math

# ----------------------
# Tile definitions
# ----------------------
WALL = 1
FLOOR = 0
EXIT = 2
MAP = 3
FOOD = 4
LIGHT = 5
GATE_CLOSED = 6
GATE_OPEN = 7

TOP_BORDER = 3
BOTTOM_BORDER = 3
LEFT_BORDER = 5
RIGHT_BORDER = 5

# ----------------------
# Cave generator
# ----------------------
def generate_cave(rows, cols,
                  room_density=0.015,
                  min_room_size=3,
                  max_room_size=6,
                  num_maps=5,
                  num_foods=10,
                  num_lights=8,
                  num_gates=6):

    cave = [[WALL for _ in range(cols)] for _ in range(rows)]

    min_x = LEFT_BORDER
    max_x = cols - RIGHT_BORDER - 1
    min_y = TOP_BORDER
    max_y = rows - BOTTOM_BORDER - 1

    # ----------------------
    # Maze generation (iterative DFS)
    # ----------------------
    start_x = min_x | 1
    start_y = min_y | 1
    cave[start_y][start_x] = FLOOR

    stack = [(start_x, start_y)]
    while stack:
        x, y = stack[-1]
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        found = False
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if min_x <= nx <= max_x and min_y <= ny <= max_y:
                if cave[ny][nx] == WALL:
                    cave[y + dy // 2][x + dx // 2] = FLOOR
                    cave[ny][nx] = FLOOR
                    stack.append((nx, ny))
                    found = True
                    break
        if not found:
            stack.pop()

    # ----------------------
    # Rooms
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

    room_attempts = int(rows * cols * room_density)
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
    exit_pos = (exit_x, exit_y)

    # ----------------------
    # Scatter items
    # ----------------------
    def scatter_item(cave, item_id, count, min_distance=4):
        rows, cols = len(cave), len(cave[0])
        placed_positions = []
        attempts = 0
        max_attempts = count * 50
        while len(placed_positions) < count and attempts < max_attempts:
            x = random.randint(LEFT_BORDER, cols - RIGHT_BORDER - 1)
            y = random.randint(TOP_BORDER, rows - BOTTOM_BORDER - 1)
            if cave[y][x] != FLOOR:
                attempts += 1
                continue
            too_close = False
            for px, py in placed_positions:
                if math.sqrt((px - x)**2 + (py - y)**2) < min_distance:
                    too_close = True
                    break
            if too_close:
                attempts += 1
                continue
            cave[y][x] = item_id
            placed_positions.append((x, y))
            attempts += 1

    scatter_item(cave, MAP, num_maps, min_distance=5)
    scatter_item(cave, FOOD, num_foods, min_distance=3)
    scatter_item(cave, LIGHT, num_lights, min_distance=4)

    # ----------------------
    # Scatter gates
    # ----------------------
    gates = []

    def scatter_gates(cave, count):
        rows, cols = len(cave), len(cave[0])
        gates_local = []
        attempts = 0
        while len(gates_local) < count and attempts < count * 50:
            x = random.randint(LEFT_BORDER, cols - RIGHT_BORDER - 1)
            y = random.randint(TOP_BORDER, rows - BOTTOM_BORDER - 1)
            if cave[y][x] == FLOOR:
                cave[y][x] = GATE_OPEN
                gates_local.append((x, y))
            attempts += 1
        return gates_local

    gates = scatter_gates(cave, num_gates)

    return cave, (spawn_x, spawn_y), gates, exit_pos

# ----------------------
# BFS helpers
# ----------------------
def find_farthest_cell(cave, start_x, start_y):
    rows, cols = len(cave), len(cave[0])
    dist = [[-1]*cols for _ in range(rows)]
    queue = deque([(start_x, start_y)])
    dist[start_y][start_x] = 0
    farthest = (start_x, start_y)
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0,-1),(1,0),(0,1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if cave[ny][nx] != WALL and dist[ny][nx] == -1:
                    dist[ny][nx] = dist[y][x] + 1
                    queue.append((nx, ny))
                    farthest = (nx, ny)
    return farthest

def path_exists(cave, start, goal):
    rows, cols = len(cave), len(cave[0])
    visited = [[False]*cols for _ in range(rows)]
    queue = deque([start])
    visited[start[1]][start[0]] = True
    walkable = {FLOOR, EXIT, MAP, FOOD, LIGHT, GATE_OPEN}
    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return True
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if not visited[ny][nx] and cave[ny][nx] in walkable:
                    visited[ny][nx] = True
                    queue.append((nx, ny))
    return False

# ----------------------
# Shuffle gates dynamically
# ----------------------
def shuffle_gates(cave, gates, player_pos, exit_pos, toggle_prob=0.5):
    """
    Randomly open/close gates but keep path to exit always valid.
    """
    original_states = { (x,y): cave[y][x] for (x,y) in gates }

    # Random toggle
    for (x,y) in gates:
        if random.random() < toggle_prob:
            cave[y][x] = GATE_CLOSED if cave[y][x] == GATE_OPEN else GATE_OPEN

    # Validate path
    if not path_exists(cave, player_pos, exit_pos):
        # Revert
        for (x,y), state in original_states.items():
            cave[y][x] = state
        return False

    return True

# ----------------------
# Print cave
# ----------------------
def print_cave(cave, spawn=None):
    tile_symbols = {
        WALL: "#",
        FLOOR: ".",
        EXIT: "E",
        MAP: "M",
        FOOD: "F",
        LIGHT: "L",
        GATE_OPEN: "O",
        GATE_CLOSED: "X"
    }
    for y, row in enumerate(cave):
        line = ""
        for x, cell in enumerate(row):
            if spawn and (x, y) == spawn:
                line += "S"
            else:
                line += tile_symbols.get(cell, "?")
        print(line)

# ----------------------
# Example usage
# ----------------------
if __name__ == "__main__":
    cave, spawn, gates, exit_pos = generate_cave(
        rows=20,
        cols=30,
        num_maps=3,
        num_foods=6,
        num_lights=5,
        num_gates=6
    )

    print("Spawn position:", spawn)
    print("Exit position:", exit_pos)
    print("Gate positions:", gates)
    print("\nInitial cave:")
    print_cave(cave, spawn)

    print("\n-- After shuffling gates (map view) --")
    shuffle_gates(cave, gates, player_pos=spawn, exit_pos=exit_pos)
    print_cave(cave, spawn)
