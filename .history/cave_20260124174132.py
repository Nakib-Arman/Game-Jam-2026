import random
from collections import deque

def generate_maze(level):
    if(level == "easy"): 
        rows, cols = 50,6
    elif (level == "medium"):
        rows, cols = 70,70
    else:
        rows, cols = 90,90

    maze = [[1 for _ in range(cols)] for _ in range(rows)]

    def carve(x, y):
        maze[y][x] = 0
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx*2, y + dy*2
            if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                carve(nx, ny)

    carve(0, 0)

    def find_farthest_cell(start_x, start_y):
        queue = deque()
        queue.append((start_x, start_y))
        distances = [[-1 for _ in range(cols)] for _ in range(rows)]
        distances[start_y][start_x] = 0

        farthest = (start_x, start_y)

        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < cols and
                    0 <= ny < rows and
                    maze[ny][nx] == 0 and
                    distances[ny][nx] == -1
                ):
                    distances[ny][nx] = distances[y][x] + 1
                    queue.append((nx, ny))
                    farthest = (nx, ny)

        return farthest

    end_x, end_y = find_farthest_cell(0, 0)
    maze[end_y][end_x] = 2

    return maze

maze_matrix = generate_maze("easy")

# Print the maze
for row in maze_matrix:
    print(row)
