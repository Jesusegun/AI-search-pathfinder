import random
from collections import deque

from config import (
    FLOOR, MUD, WALL,
    DEFAULT_WALL_PERCENT, DEFAULT_MUD_PERCENT
)
from grid import Grid


def _randomize_endpoints(grid):
    """Place start and goal on random FLOOR cells with meaningful separation.
    
    Picks two random walkable cells whose Manhattan distance is at least
    (width + height) / 3 so the path is non-trivial.
    
    @param grid: The Grid object to modify in-place.
    @return: None
    """
    floor_cells = []
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.get_cell(x, y)
            if cell.terrain == FLOOR:
                floor_cells.append(cell)
    
    if len(floor_cells) < 2:
        return
    
    min_distance = (grid.width + grid.height) // 3
    best_pair = None
    best_dist = 0
    
    max_tries = 200
    for _ in range(max_tries):
        a, b = random.sample(floor_cells, 2)
        dist = abs(a.x - b.x) + abs(a.y - b.y)
        if dist >= min_distance:
            grid.start = a
            grid.goal = b
            return
        if dist > best_dist:
            best_dist = dist
            best_pair = (a, b)
    
    # Fallback: use the best pair found
    if best_pair:
        grid.start = best_pair[0]
        grid.goal = best_pair[1]


def generate_random_maze(width, height, wall_percent=DEFAULT_WALL_PERCENT, 
                         mud_percent=DEFAULT_MUD_PERCENT):
    grid = Grid(width, height)
    
    total_cells = width * height
    num_walls = int(total_cells * wall_percent)
    
    walls_placed = 0
    attempts = 0
    max_attempts = num_walls * 4
    
    while walls_placed < num_walls and attempts < max_attempts:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        
        cell = grid.get_cell(x, y)
        
        if cell != grid.start and cell != grid.goal and cell.terrain == FLOOR:
            if not _would_block_start_goal(grid, x, y):
                grid.set_terrain(x, y, WALL)
                walls_placed += 1
        
        attempts += 1
    
    for y in range(height):
        for x in range(width):
            cell = grid.get_cell(x, y)
            if cell.terrain == FLOOR and cell != grid.start and cell != grid.goal:
                if random.random() < mud_percent:
                    grid.set_terrain(x, y, MUD)
    
    _randomize_endpoints(grid)
    return grid


def _would_block_start_goal(grid, x, y):
    start = grid.start
    goal = grid.goal
    
    if abs(x - start.x) + abs(y - start.y) <= 1:
        neighbors = grid.get_neighbors(start)
        if len(neighbors) <= 2:
            return True
    
    if abs(x - goal.x) + abs(y - goal.y) <= 1:
        neighbors = grid.get_neighbors(goal)
        if len(neighbors) <= 2:
            return True
    
    return False


def generate_recursive_backtracker(width, height, mud_percent=DEFAULT_MUD_PERCENT):
    grid = Grid(width, height)
    
    for y in range(height):
        for x in range(width):
            grid.set_terrain(x, y, WALL)
    
    start_x = 1 if width > 1 else 0
    start_y = 1 if height > 1 else 0
    
    grid.set_terrain(start_x, start_y, FLOOR)
    
    stack = [(start_x, start_y)]
    visited = {(start_x, start_y)}
    
    directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
    
    while stack:
        current_x, current_y = stack[-1]
        
        neighbors = []
        for dx, dy in directions:
            nx, ny = current_x + dx, current_y + dy
            if (1 <= nx < width - 1 and 1 <= ny < height - 1 and 
                (nx, ny) not in visited):
                neighbors.append((nx, ny, dx // 2, dy // 2))
        
        if neighbors:
            nx, ny, wall_dx, wall_dy = random.choice(neighbors)
            
            grid.set_terrain(nx, ny, FLOOR)
            grid.set_terrain(current_x + wall_dx, current_y + wall_dy, FLOOR)
            
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            stack.pop()
    
    grid.start = grid.get_cell(1, 1)
    grid.goal = grid.get_cell(width - 2 if width % 2 == 1 else width - 3,
                               height - 2 if height % 2 == 1 else height - 3)
    
    for y in range(height):
        for x in range(width):
            cell = grid.get_cell(x, y)
            if (cell.terrain == FLOOR and 
                cell != grid.start and cell != grid.goal):
                if random.random() < mud_percent:
                    grid.set_terrain(x, y, MUD)
    
    return grid


def generate_open_maze(width, height, wall_percent=0.20, mud_percent=0.25):
    grid = Grid(width, height)
    
    total_cells = width * height
    target_walls = int(total_cells * wall_percent)
    walls_placed = 0
    
    # Initially protect only the default start/goal from walls
    default_protected = {
        (grid.start.x, grid.start.y),
        (grid.goal.x, grid.goal.y),
    }
    
    eligible_cells = []
    for y in range(height):
        for x in range(width):
            if (x, y) not in default_protected:
                eligible_cells.append((x, y))
    
    random.shuffle(eligible_cells)
    
    for x, y in eligible_cells:
        if walls_placed >= target_walls:
            break
        
        if random.random() < 0.7:
            grid.set_terrain(x, y, WALL)
            walls_placed += 1
    
    # Randomize start/goal AFTER walls so they land on floor cells
    _randomize_endpoints(grid)
    
    # Build protected set around the NEW start/goal for mud placement
    protected = set()
    protected.add((grid.start.x, grid.start.y))
    protected.add((grid.goal.x, grid.goal.y))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        protected.add((grid.start.x + dx, grid.start.y + dy))
        protected.add((grid.goal.x + dx, grid.goal.y + dy))
    
    target_mud = int(total_cells * mud_percent)
    mud_placed = 0
    
    for y in range(height):
        for x in range(width):
            if mud_placed >= target_mud:
                break
            cell = grid.get_cell(x, y)
            if cell.terrain == FLOOR and (x, y) not in protected:
                if random.random() < 0.35:
                    grid.set_terrain(x, y, MUD)
                    mud_placed += 1
    
    for i in range(min(width, height) // 2):
        x = random.randint(2, width - 3)
        y = random.randint(2, height - 3)
        cell = grid.get_cell(x, y)
        if cell.terrain == FLOOR and (x, y) not in protected:
            grid.set_terrain(x, y, MUD)
    
    return grid


def path_exists(grid):
    if grid.start == grid.goal:
        return True
    
    frontier = deque([grid.start])
    visited = {grid.start}
    
    while frontier:
        current = frontier.popleft()
        
        if current == grid.goal:
            return True
        
        for neighbor in grid.get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.append(neighbor)
    
    return False


def generate_maze(width, height, maze_type="random", **kwargs):
    if maze_type == "recursive":
        return generate_recursive_backtracker(width, height, **kwargs)
    elif maze_type == "open":
        return generate_open_maze(width, height, **kwargs)
    else:
        return generate_random_maze(width, height, **kwargs)
