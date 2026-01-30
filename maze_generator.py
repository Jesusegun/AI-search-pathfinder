"""
Maze generation algorithms for the pathfinding arena.

This module provides maze generation including:
- Random maze with configurable wall/mud density
- Recursive backtracker for perfect mazes
- Path existence verification

@author: CPS 170 AI Course Project
"""

import random
from collections import deque

from config import (
    FLOOR, MUD, WALL,
    DEFAULT_WALL_PERCENT, DEFAULT_MUD_PERCENT
)
from grid import Grid


def generate_random_maze(width, height, wall_percent=DEFAULT_WALL_PERCENT, 
                         mud_percent=DEFAULT_MUD_PERCENT):
    """
    Generate a random maze with walls and mud.
    
    Creates an open grid with randomly placed walls and mud patches.
    Ensures start and goal remain clear.
    
    @param width: Grid width
    @param height: Grid height
    @param wall_percent: Percentage of cells that are walls (0.0 to 1.0)
    @param mud_percent: Percentage of remaining cells that are mud
    @return: Generated Grid object
    """
    grid = Grid(width, height)
    
    # Calculate number of walls to place
    total_cells = width * height
    num_walls = int(total_cells * wall_percent)
    
    # Place walls randomly
    walls_placed = 0
    attempts = 0
    max_attempts = num_walls * 4  # Prevent infinite loop
    
    while walls_placed < num_walls and attempts < max_attempts:
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        
        cell = grid.get_cell(x, y)
        
        # Don't place walls on start, goal, or existing walls
        if cell != grid.start and cell != grid.goal and cell.terrain == FLOOR:
            # Don't completely block start or goal
            if not _would_block_start_goal(grid, x, y):
                grid.set_terrain(x, y, WALL)
                walls_placed += 1
        
        attempts += 1
    
    # Add mud to remaining floor cells
    for y in range(height):
        for x in range(width):
            cell = grid.get_cell(x, y)
            if cell.terrain == FLOOR and cell != grid.start and cell != grid.goal:
                if random.random() < mud_percent:
                    grid.set_terrain(x, y, MUD)
    
    # Verify path exists, if not regenerate
    if not path_exists(grid):
        return generate_random_maze(width, height, 
                                    wall_percent * 0.9,  # Reduce walls
                                    mud_percent)
    
    return grid


def _would_block_start_goal(grid, x, y):
    """
    Check if placing a wall here would completely block start or goal.
    
    @param grid: The grid
    @param x: X coordinate to check
    @param y: Y coordinate to check
    @return: True if placement would block, False otherwise
    """
    # Check if adjacent to start with limited neighbors
    start = grid.start
    goal = grid.goal
    
    # Don't wall off directly adjacent to start/goal
    if abs(x - start.x) + abs(y - start.y) <= 1:
        # Count remaining walkable neighbors for start
        neighbors = grid.get_neighbors(start)
        if len(neighbors) <= 2:
            return True
    
    if abs(x - goal.x) + abs(y - goal.y) <= 1:
        neighbors = grid.get_neighbors(goal)
        if len(neighbors) <= 2:
            return True
    
    return False


def generate_recursive_backtracker(width, height, mud_percent=DEFAULT_MUD_PERCENT):
    """
    Generate a perfect maze using recursive backtracker algorithm.
    
    Creates a maze with guaranteed solution path using DFS-based
    maze carving. Results in long, winding corridors.
    
    @param width: Grid width (should be odd for best results)
    @param height: Grid height (should be odd for best results)
    @param mud_percent: Percentage of floor cells to convert to mud
    @return: Generated Grid object
    """
    grid = Grid(width, height)
    
    # Initialize all cells as walls
    for y in range(height):
        for x in range(width):
            grid.set_terrain(x, y, WALL)
    
    # Starting position for carving (must be odd coordinates)
    start_x = 1 if width > 1 else 0
    start_y = 1 if height > 1 else 0
    
    # Carve starting position
    grid.set_terrain(start_x, start_y, FLOOR)
    
    # Stack for backtracking
    stack = [(start_x, start_y)]
    visited = {(start_x, start_y)}
    
    # Directions: Up, Right, Down, Left (skip 2 cells)
    directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
    
    while stack:
        current_x, current_y = stack[-1]
        
        # Find unvisited neighbors (2 cells away)
        neighbors = []
        for dx, dy in directions:
            nx, ny = current_x + dx, current_y + dy
            if (1 <= nx < width - 1 and 1 <= ny < height - 1 and 
                (nx, ny) not in visited):
                neighbors.append((nx, ny, dx // 2, dy // 2))
        
        if neighbors:
            # Choose random unvisited neighbor
            nx, ny, wall_dx, wall_dy = random.choice(neighbors)
            
            # Carve passage
            grid.set_terrain(nx, ny, FLOOR)
            grid.set_terrain(current_x + wall_dx, current_y + wall_dy, FLOOR)
            
            visited.add((nx, ny))
            stack.append((nx, ny))
        else:
            # Backtrack
            stack.pop()
    
    # Set start and goal in carved areas
    grid.start = grid.get_cell(1, 1)
    grid.goal = grid.get_cell(width - 2 if width % 2 == 1 else width - 3,
                               height - 2 if height % 2 == 1 else height - 3)
    
    # Add mud to some floor cells
    for y in range(height):
        for x in range(width):
            cell = grid.get_cell(x, y)
            if (cell.terrain == FLOOR and 
                cell != grid.start and cell != grid.goal):
                if random.random() < mud_percent:
                    grid.set_terrain(x, y, MUD)
    
    return grid


def generate_open_maze(width, height, wall_percent=0.20, mud_percent=0.25):
    """
    Generate an open maze with scattered obstacles.
    
    Good for demonstrating algorithm differences clearly.
    Ensures obstacles appear throughout including along direct paths.
    
    @param width: Grid width
    @param height: Grid height
    @param wall_percent: Percentage of wall cells
    @param mud_percent: Percentage of mud cells
    @return: Generated Grid object
    """
    grid = Grid(width, height)
    
    # Protected cells: start, goal, and their immediate neighbors
    protected = set()
    protected.add((grid.start.x, grid.start.y))
    protected.add((grid.goal.x, grid.goal.y))
    # Protect immediate neighbors of start and goal (leave at least one exit)
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        protected.add((grid.start.x + dx, grid.start.y + dy))
        protected.add((grid.goal.x + dx, grid.goal.y + dy))
    
    # Place walls randomly throughout the grid
    total_cells = width * height
    target_walls = int(total_cells * wall_percent)
    walls_placed = 0
    
    # Create a shuffled list of all interior cells
    interior_cells = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if (x, y) not in protected:
                interior_cells.append((x, y))
    
    random.shuffle(interior_cells)
    
    # Place walls from shuffled list
    for x, y in interior_cells:
        if walls_placed >= target_walls:
            break
        
        # Place wall with some randomness
        if random.random() < 0.7:  # 70% chance to actually place
            grid.set_terrain(x, y, WALL)
            walls_placed += 1
    
    # Add mud patches scattered throughout
    target_mud = int(total_cells * mud_percent)
    mud_placed = 0
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if mud_placed >= target_mud:
                break
            cell = grid.get_cell(x, y)
            if cell.terrain == FLOOR and (x, y) not in protected:
                if random.random() < 0.35:  # Random chance for variety
                    grid.set_terrain(x, y, MUD)
                    mud_placed += 1
    
    # Add some strategic mud patches along the "direct" path
    # This makes A* vs BFS comparison more interesting
    for i in range(min(width, height) // 2):
        # Along diagonal-ish path from start to goal
        x = random.randint(2, width - 3)
        y = random.randint(2, height - 3)
        cell = grid.get_cell(x, y)
        if cell.terrain == FLOOR and (x, y) not in protected:
            grid.set_terrain(x, y, MUD)
    
    # Verify path exists - regenerate with fewer walls if blocked
    if not path_exists(grid):
        return generate_open_maze(width, height, wall_percent * 0.7, mud_percent)
    
    return grid


def path_exists(grid):
    """
    Check if a path exists from start to goal using BFS.
    
    @param grid: Grid to check
    @return: True if path exists, False otherwise
    """
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
    """
    Generate a maze of the specified type.
    
    @param width: Grid width
    @param height: Grid height
    @param maze_type: Type of maze ("random", "recursive", "open")
    @param kwargs: Additional parameters for specific generators
    @return: Generated Grid object
    """
    if maze_type == "recursive":
        return generate_recursive_backtracker(width, height, **kwargs)
    elif maze_type == "open":
        return generate_open_maze(width, height, **kwargs)
    else:
        return generate_random_maze(width, height, **kwargs)
