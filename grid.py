from config import (
    GRID_WIDTH, GRID_HEIGHT, FLOOR, MUD, WALL,
    COST_FLOOR, COST_MUD, COST_WALL
)


class Cell:
    __slots__ = ['x', 'y', 'terrain']
    
    def __init__(self, x, y, terrain=FLOOR):
        self.x = x
        self.y = y
        self.terrain = terrain
    
    def __eq__(self, other):
        if other is None:
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        terrain_names = {FLOOR: 'FLOOR', MUD: 'MUD', WALL: 'WALL'}
        return f"Cell({self.x}, {self.y}, {terrain_names.get(self.terrain, '?')})"
    
    def __lt__(self, other):
        return (self.x, self.y) < (other.x, other.y)
    
    def copy(self):
        return Cell(self.x, self.y, self.terrain)


class Grid:
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, y) for x in range(width)] for y in range(height)]
        
        self.start = self.cells[1][1]
        self.goal = self.cells[height - 2][width - 2]
    
    def get_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None
    
    def set_terrain(self, x, y, terrain):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x].terrain = terrain
    
    def get_neighbors(self, cell):
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            neighbor = self.get_cell(cell.x + dx, cell.y + dy)
            if neighbor is not None and neighbor.terrain != WALL:
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_all_neighbors(self, cell):
        neighbors = []
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            neighbor = self.get_cell(cell.x + dx, cell.y + dy)
            if neighbor is not None:
                neighbors.append(neighbor)
        
        return neighbors
    
    def get_cost(self, from_cell, to_cell):
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
        if cell is None:
            return False
        return cell.terrain != WALL
    
    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.cells[y][x].terrain = FLOOR
    
    def copy(self):
        new_grid = Grid(self.width, self.height)
        for y in range(self.height):
            for x in range(self.width):
                new_grid.cells[y][x].terrain = self.cells[y][x].terrain
        
        new_grid.start = new_grid.get_cell(self.start.x, self.start.y)
        new_grid.goal = new_grid.get_cell(self.goal.x, self.goal.y)
        
        return new_grid
    
    def count_terrain(self, terrain_type):
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x].terrain == terrain_type:
                    count += 1
        return count
