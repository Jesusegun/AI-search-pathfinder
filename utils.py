import math


def heuristic_manhattan(cell, goal):
    return abs(cell.x - goal.x) + abs(cell.y - goal.y)


def heuristic_euclidean(cell, goal):
    return math.sqrt((cell.x - goal.x) ** 2 + (cell.y - goal.y) ** 2)


def heuristic(cell, goal):
    return heuristic_manhattan(cell, goal)


def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return []
    
    path = []
    current = goal
    
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    
    path.reverse()
    return path


def calculate_path_cost(path, grid):
    if not path or len(path) < 2:
        return 0
    
    total_cost = 0
    for i in range(len(path) - 1):
        total_cost += grid.get_cost(path[i], path[i + 1])
    
    return total_cost


def format_time(seconds):
    if seconds >= 1:
        return f"{seconds:.2f}s"
    else:
        return f"{seconds * 1000:.0f}ms"


def format_number(num):
    return f"{num:,}"


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(color1, color2, t):
    r = int(lerp(color1[0], color2[0], t))
    g = int(lerp(color1[1], color2[1], t))
    b = int(lerp(color1[2], color2[2], t))
    return (r, g, b)
