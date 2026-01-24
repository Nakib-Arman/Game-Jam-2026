import random

def generate_maze(level):
    if(level == "easy"): 
        rows, cols = 5,5
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
    return maze

maze_matrix = generate_maze("easy")

# Print the maze
for row in maze_matrix:
    print(row)
