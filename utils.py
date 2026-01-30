"""
Utility functions for the pathfinding algorithms.

This module provides helper functions including:
- Heuristic calculations (Manhattan, Euclidean)
- Path reconstruction
- Cost calculations

@author: CPS 170 AI Course Project
"""

import math


def heuristic_manhattan(cell, goal):
    """
    Calculate Manhattan distance heuristic.
    
    Manhattan distance is admissible for 4-directional movement.
    h(n) = |x1 - x2| + |y1 - y2|
    
    @param cell: Current cell
    @param goal: Goal cell
    @return: Manhattan distance to goal
    """
    return abs(cell.x - goal.x) + abs(cell.y - goal.y)


def heuristic_euclidean(cell, goal):
    """
    Calculate Euclidean distance heuristic.
    
    Euclidean distance is admissible for 8-directional movement.
    h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)
    
    @param cell: Current cell
    @param goal: Goal cell
    @return: Euclidean distance to goal
    """
    return math.sqrt((cell.x - goal.x) ** 2 + (cell.y - goal.y) ** 2)


def heuristic(cell, goal):
    """
    Default heuristic function (Manhattan distance).
    
    @param cell: Current cell
    @param goal: Goal cell
    @return: Heuristic estimate to goal
    """
    return heuristic_manhattan(cell, goal)


def reconstruct_path(came_from, start, goal):
    """
    Reconstruct path from came_from dictionary.
    
    Traces back from goal to start using parent pointers.
    
    @param came_from: Dictionary mapping each cell to its parent
    @param start: Starting cell
    @param goal: Goal cell
    @return: List of cells from start to goal, or empty list if no path
    """
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
    """
    Calculate total cost of traversing a path.
    
    Sums up the terrain costs for each step in the path.
    
    @param path: List of cells representing the path
    @param grid: The grid containing terrain information
    @return: Total path cost
    """
    if not path or len(path) < 2:
        return 0
    
    total_cost = 0
    for i in range(len(path) - 1):
        total_cost += grid.get_cost(path[i], path[i + 1])
    
    return total_cost


def format_time(seconds):
    """
    Format time in seconds to a readable string.
    
    @param seconds: Time in seconds
    @return: Formatted string (e.g., "1.23s" or "45ms")
    """
    if seconds >= 1:
        return f"{seconds:.2f}s"
    else:
        return f"{seconds * 1000:.0f}ms"


def format_number(num):
    """
    Format large numbers with commas.
    
    @param num: Number to format
    @return: Formatted string (e.g., "1,234")
    """
    return f"{num:,}"


def clamp(value, min_val, max_val):
    """
    Clamp a value between min and max.
    
    @param value: Value to clamp
    @param min_val: Minimum allowed value
    @param max_val: Maximum allowed value
    @return: Clamped value
    """
    return max(min_val, min(max_val, value))


def lerp(a, b, t):
    """
    Linear interpolation between two values.
    
    @param a: Start value
    @param b: End value
    @param t: Interpolation factor (0.0 to 1.0)
    @return: Interpolated value
    """
    return a + (b - a) * t


def lerp_color(color1, color2, t):
    """
    Linear interpolation between two RGB colors.
    
    @param color1: Start color (R, G, B)
    @param color2: End color (R, G, B)
    @param t: Interpolation factor (0.0 to 1.0)
    @return: Interpolated color (R, G, B)
    """
    r = int(lerp(color1[0], color2[0], t))
    g = int(lerp(color1[1], color2[1], t))
    b = int(lerp(color1[2], color2[2], t))
    return (r, g, b)
