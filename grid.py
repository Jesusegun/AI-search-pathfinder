"""
Grid and Cell data structures for the pathfinding arena.

This module provides:
- Cell: Represents a single grid cell with position and terrain
- Grid: 2D grid structure with neighbor/cost calculations

@author: CPS 170 AI Course Project
"""

from config import (
    GRID_WIDTH, GRID_HEIGHT, FLOOR, MUD, WALL,
    COST_FLOOR, COST_MUD, COST_WALL
)


class Cell:
    """
    Represents a single cell in the pathfinding grid.
    
    Attributes:
        x (int): X coordinate (column)
        y (int): Y coordinate (row)
        terrain (int): Terrain type (FLOOR, MUD, or WALL)
    """
    
    __slots__ = ['x', 'y', 'terrain']
    
    def __init__(self, x, y, terrain=FLOOR):
        """
        Initialize a cell.
        
        @param x: X coordinate (column)
        @param y: Y coordinate (row)
        @param terrain: Terrain type, default is FLOOR
        """
        self.x = x
        self.y = y
        self.terrain = terrain
    
    def __eq__(self, other):
        """Check equality based on position."""
        if other is None:
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        """Hash based on position for use in sets/dicts."""
        return hash((self.x, self.y))
    
    def __repr__(self):
        """String representation for debugging."""
        terrain_names = {FLOOR: 'FLOOR', MUD: 'MUD', WALL: 'WALL'}
        return f"Cell({self.x}, {self.y}, {terrain_names.get(self.terrain, '?')})"
    
    def __lt__(self, other):
        """Less-than comparison for heap operations."""
        return (self.x, self.y) < (other.x, other.y)
    
    def copy(self):
        """
        Create a copy of this cell.
        
        @return: New Cell with same properties
        """
        return Cell(self.x, self.y, self.terrain)


class Grid:
    """
    2D grid structure for the pathfinding maze.
    
    Handles terrain, neighbors, and movement costs.
    
    Attributes:
        width (int): Grid width in cells
        height (int): Grid height in cells
        cells (list): 2D array of Cell objects
        start (Cell): Starting position
        goal (Cell): Goal position
    """
    
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        """
        Initialize an empty grid.
        
        @param width: Grid width in cells
        @param height: Grid height in cells
        """
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y) for x in range(width)] for y in range(height)]
        
        # Default start (top-left area) and goal (bottom-right area)
        self.start = self.cells[1][1]
        self.goal = self.cells[height - 2][width - 2]
    
    def get_cell(self, x, y):
        """
        Get cell at specified coordinates.
        
        @param x: X coordinate (column)
        @param y: Y coordinate (row)
        @return: Cell at (x, y) or None if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None
    
    def set_terrain(self, x, y, terrain):
        """
        Set terrain type at specified coordinates.
        
        @param x: X coordinate
        @param y: Y coordinate
        @param terrain: Terrain type (FLOOR, MUD, WALL)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x].terrain = terrain
    
    def get_neighbors(self, cell):
        """
        Get all walkable neighbors of a cell (4-directional).
        
        @param cell: The cell to find neighbors for
        @return: List of walkable neighboring cells
        """
        neighbors = []
        # Up, Right, Down, Left
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            neighbor = self.get_cell(cell.x + dx, cell.y + dy)
            if neighbor is not None and neighbor.terrain != WALL:
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_all_neighbors(self, cell):
        """
        Get all neighbors including walls (for visualization).
        
        @param cell: The cell to find neighbors for
        @return: List of all neighboring cells
        """
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            neighbor = self.get_cell(cell.x + dx, cell.y + dy)
            if neighbor is not None:
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_cost(self, from_cell, to_cell):
        """
        Get movement cost between adjacent cells.
        
        Cost is based on the destination cell's terrain.
        
        @param from_cell: Starting cell
        @param to_cell: Destination cell
        @return: Movement cost (1 for floor, 5 for mud, inf for wall)
        """
        if to_cell is None:
            return COST_WALL
        
        if to_cell.terrain == FLOOR:
            return COST_FLOOR
        elif to_cell.terrain == MUD:
            return COST_MUD
        elif to_cell.terrain == WALL:
            return COST_WALL
        
        return COST_FLOOR
    
    def is_walkable(self, cell):
        """
        Check if a cell is walkable (not a wall).
        
        @param cell: Cell to check
        @return: True if walkable, False otherwise
        """
        if cell is None:
            return False
        return cell.terrain != WALL
    
    def is_valid_position(self, x, y):
        """
        Check if coordinates are within grid bounds.
        
        @param x: X coordinate
        @param y: Y coordinate
        @return: True if valid, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height
    
    def clear(self):
        """Reset all cells to FLOOR terrain."""
        for y in range(self.height):
            for x in range(self.width):
                self.cells[y][x].terrain = FLOOR
    
    def copy(self):
        """
        Create a deep copy of the grid.
        
        @return: New Grid with copied cells
        """
        new_grid = Grid(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                new_grid.cells[y][x].terrain = self.cells[y][x].terrain
        
        new_grid.start = new_grid.get_cell(self.start.x, self.start.y)
        new_grid.goal = new_grid.get_cell(self.goal.x, self.goal.y)
        
        return new_grid
    
    def count_terrain(self, terrain_type):
        """
        Count cells of a specific terrain type.
        
        @param terrain_type: Terrain type to count
        @return: Number of cells with that terrain
        """
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x].terrain == terrain_type:
                    count += 1
        return count
