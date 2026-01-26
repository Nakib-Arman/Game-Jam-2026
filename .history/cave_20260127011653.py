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


def generate_cave(rows, cols,
                  room_density=0.015,   # room generation density
                  min_room_size=3,
                  max_room_size=6,
                  num_maps=5,           # number of maps to scatter
                  num_foods=10,         # number of foods to scatter
                  num_lights=8):        # number of lights to scatter

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
                distance = math.sqrt((px - x)**2 + (py - y)**2)
                if distance < min_distance:
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
    # Place gates in narrow passages
    # ----------------------
    place_gates(cave, spawn=(spawn_x, spawn_y), exit_pos=(exit_x, exit_y))

    return cave, (spawn_x, spawn_y)


# ----------------------
# Find farthest cell
# ----------------------
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


# ----------------------
# Gate placement
# ----------------------
def place_gates(cave, spawn, exit_pos, gate_chance=0.15):
    """
    Place gates in narrow corridors (1-tile wide) randomly.
    """
    rows, cols = len(cave), len(cave[0])
    for y in range(1, rows-1):
        for x in range(1, cols-1):
            if cave[y][x] != FLOOR:
                continue

            # Narrow corridor check (exactly 2 floors adjacent)
            adjacent = sum([cave[y+dy][x+dx]==FLOOR for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]])
            if adjacent == 2 and random.random() < gate_chance:
                cave[y][x] = GATE_CLOSED

    # Ensure path from spawn to exit remains (open gates along path)
    open_path_between(cave, spawn, exit_pos)


def open_path_between(cave, start, end):
    """
    Ensure a path from start to end exists by opening any gates along the path.
    """
    path = bfs_path(cave, start, end)
    if not path:
        return
    for x, y in path:
        if cave[y][x] == GATE_CLOSED:
            cave[y][x] = GATE_OPEN


def bfs_path(cave, start, end):
    """
    Simple BFS pathfinding from start to end avoiding walls.
    Returns list of coordinates in path.
    """
    rows, cols = len(cave), len(cave[0])
    queue = deque([start])
    prev = {start: None}

    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) == end:
            break
        for dx, dy in [(0,1),(1,0),(0,-1),(-1,0)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cols and 0 <= ny < rows:
                if cave[ny][nx] not in (WALL,) and (nx, ny) not in prev:
                    queue.append((nx, ny))
                    prev[(nx, ny)] = (cx, cy)

    # Reconstruct path
    if end not in prev:
        return []
    path = []
    current = end
    while current != start:
        path.append(current)
        current = prev[current]
    path.append(start)
    path.reverse()
    return path


# ----------------------
# Rearrange gates dynamically
# ----------------------
def rearrange_gates(cave, spawn, exit_pos, open_ratio=0.5):
    """
    Randomly toggle gates in the cave while keeping a guaranteed path from spawn to exit.
    open_ratio: fraction of gates to keep open
    """
    gate_positions = [(x, y) for y, row in enumerate(cave) for x, cell in enumerate(row) if cell in (GATE_CLOSED, GATE_OPEN)]

    # Shuffle and set gates
    random.shuffle(gate_positions)
    num_open = int(len(gate_positions) * open_ratio)
    for i, (x, y) in enumerate(gate_positions):
        cave[y][x] = GATE_OPEN if i < num_open else GATE_CLOSED

    # Open gates along guaranteed path
    open_path_between(cave, spawn, exit_pos)


def toggle_gates_randomly(cave, player_pos, exit_pos, open_ratio=0.5):
    """
    Randomly open/close gates while ensuring a path from player to exit remains.
    - cave: 2D list of tiles
    - player_pos: (x, y) tile coordinates
    - exit_pos: (x, y) tile coordinates
    - open_ratio: fraction of gates that will remain open
    """
    from collections import deque
    import random

    rows, cols = len(cave), len(cave[0])

    # Get all gates positions
    gates = [(x, y) for y in range(rows) for x in range(cols) if cave[y][x] in (6, 7)]

    # Shuffle the gates
    random.shuffle(gates)

    # Close all gates first
    for x, y in gates:
        cave[y][x] = 6  # closed

    # Open a fraction of gates
    num_to_open = max(1, int(len(gates) * open_ratio))
    for i in range(num_to_open):
        x, y = gates[i]
        cave[y][x] = 7  # open

    # Ensure there is still a path from player to exit
    # BFS to check path
    queue = deque([player_pos])
    visited = set([player_pos])
    while queue:
        x, y = queue.popleft()
        if (x, y) == exit_pos:
            return  # path exists
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0<=nx<cols and 0<=ny<rows and (nx, ny) not in visited:
                if cave[ny][nx] in (0, 2, 7, 3, 4, 5):  # passable tiles
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    # If path doesn't exist, open gates along first BFS path
    # Simple fix: open all gates along BFS from player
    for x, y in gates:
        if (x, y) not in visited:
            cave[y][x] = 7



# ----------------------
# Print cave for debugging
# ----------------------
def print_cave(cave, spawn=None):
    tile_symbols = {
        WALL: "#",
        FLOOR: ".",
        EXIT: "E",
        MAP: "M",
        FOOD: "F",
        LIGHT: "L",
        GATE_CLOSED: "X",
        GATE_OPEN: "O"
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
    cave, spawn = generate_cave(
        rows=20,
        cols=30,
        num_maps=3,
        num_foods=6,
        num_lights=5
    )
    exit_pos = find_farthest_cell(cave, spawn[0], spawn[1])
    print("Spawn:", spawn, "Exit:", exit_pos)
    print_cave(cave, spawn)

    print("\n--- Rearranging gates ---\n")
    rearrange_gates(cave, spawn, exit_pos, open_ratio=0.4)
    print_cave(cave, spawn)
