"""
Visualization module for the pathfinding racing arena.

This module handles:
- Grid rendering with terrain colors
- Path and exploration visualization
- Particle trail effects
- Animation management

@author: CPS 170 AI Course Project
"""

import pygame
from config import (
    CELL_SIZE, FLOOR, MUD, WALL,
    COLOR_FLOOR, COLOR_MUD, COLOR_WALL, COLOR_GRID_LINE,
    COLOR_START, COLOR_GOAL,
    COLOR_A_EXPLORED, COLOR_A_PATH, COLOR_A_CURRENT,
    COLOR_B_EXPLORED, COLOR_B_PATH, COLOR_B_CURRENT,
    PARTICLE_LIFETIME, PARTICLE_SIZE,
    LEFT_GRID_X, RIGHT_GRID_X, GRID_Y
)
from utils import lerp


class Particle:
    """
    Fading particle for trail effects.
    
    Particles are created when cells are explored and fade over time.
    
    Attributes:
        x, y: Screen position
        color: Base RGB color
        lifetime: Remaining frames
        max_lifetime: Initial lifetime for alpha calculation
    """
    
    __slots__ = ['x', 'y', 'color', 'lifetime', 'max_lifetime', 'size']
    
    def __init__(self, x, y, color, lifetime=PARTICLE_LIFETIME):
        """
        Initialize a particle.
        
        @param x: Screen X position
        @param y: Screen Y position
        @param color: RGB color tuple
        @param lifetime: Number of frames to live
        """
        self.x = x
        self.y = y
        self.color = color[:3] if len(color) > 3 else color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = PARTICLE_SIZE
    
    def update(self):
        """Update particle state (decrease lifetime)."""
        self.lifetime -= 1
    
    def is_dead(self):
        """Check if particle should be removed."""
        return self.lifetime <= 0
    
    def get_alpha(self):
        """Calculate current alpha based on remaining lifetime."""
        return int(255 * (self.lifetime / self.max_lifetime))
    
    def draw(self, surface):
        """
        Draw particle to surface with fading effect.
        
        @param surface: Pygame surface to draw on
        """
        if self.is_dead():
            return
        
        alpha = self.get_alpha()
        size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        
        # Create a temporary surface for alpha blending
        temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.circle(temp_surface, color_with_alpha, (size, size), size)
        surface.blit(temp_surface, (self.x - size, self.y - size))


class Visualizer:
    """
    Main visualization class for rendering the racing arena.
    
    Handles grid drawing, path visualization, and particle effects.
    
    Attributes:
        screen: Pygame display surface
        particles_a: Particle list for algorithm A
        particles_b: Particle list for algorithm B
        font_small: Small font for cell labels
    """
    
    def __init__(self, screen):
        """
        Initialize the visualizer.
        
        @param screen: Pygame display surface
        """
        self.screen = screen
        self.particles_a = []
        self.particles_b = []
        
        # Initialize fonts
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 14)
    
    def draw_grid(self, grid, offset_x, offset_y, show_grid_lines=True):
        """
        Draw the maze grid with terrain colors.
        
        @param grid: Grid object to render
        @param offset_x: X offset for grid position
        @param offset_y: Y offset for grid position
        @param show_grid_lines: Whether to draw grid lines
        """
        for y in range(grid.height):
            for x in range(grid.width):
                cell = grid.get_cell(x, y)
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE,
                    offset_y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                
                # Determine terrain color
                if cell.terrain == FLOOR:
                    color = COLOR_FLOOR
                elif cell.terrain == MUD:
                    color = COLOR_MUD
                elif cell.terrain == WALL:
                    color = COLOR_WALL
                else:
                    color = COLOR_FLOOR
                
                pygame.draw.rect(self.screen, color, rect)
                
                # Draw grid lines
                if show_grid_lines:
                    pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)
        
        # Draw start marker
        self._draw_marker(grid.start, offset_x, offset_y, COLOR_START, "S")
        
        # Draw goal marker
        self._draw_marker(grid.goal, offset_x, offset_y, COLOR_GOAL, "G")
    
    def _draw_marker(self, cell, offset_x, offset_y, color, label):
        """
        Draw a labeled marker on a cell.
        
        @param cell: Cell to mark
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param color: Marker color
        @param label: Text label (e.g., "S" or "G")
        """
        rect = pygame.Rect(
            offset_x + cell.x * CELL_SIZE + 2,
            offset_y + cell.y * CELL_SIZE + 2,
            CELL_SIZE - 4,
            CELL_SIZE - 4
        )
        pygame.draw.rect(self.screen, color, rect, border_radius=3)
        
        # Draw label
        text = self.font_small.render(label, True, (0, 0, 0))
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_explored(self, explored, offset_x, offset_y, color, alpha=100):
        """
        Draw explored cells with semi-transparent overlay.
        
        @param explored: Set of explored cells
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param color: Overlay color
        @param alpha: Transparency (0-255)
        """
        overlay = pygame.Surface((CELL_SIZE - 2, CELL_SIZE - 2), pygame.SRCALPHA)
        overlay_color = (*color[:3], alpha) if len(color) >= 3 else (*color, alpha)
        overlay.fill(overlay_color)
        
        for cell in explored:
            x = offset_x + cell.x * CELL_SIZE + 1
            y = offset_y + cell.y * CELL_SIZE + 1
            self.screen.blit(overlay, (x, y))
    
    def draw_frontier(self, frontier, offset_x, offset_y, color):
        """
        Draw frontier cells with border.
        
        @param frontier: List of frontier cells
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param color: Border color
        """
        for cell in frontier:
            if hasattr(cell, 'x'):  # Cell object
                cell_to_draw = cell
            elif isinstance(cell, tuple) and len(cell) >= 2:
                # (cost, cell) or (cost, counter, cell) tuple from priority queue
                cell_to_draw = cell[-1] if hasattr(cell[-1], 'x') else cell[1]
            else:
                continue
            
            rect = pygame.Rect(
                offset_x + cell_to_draw.x * CELL_SIZE + 1,
                offset_y + cell_to_draw.y * CELL_SIZE + 1,
                CELL_SIZE - 2,
                CELL_SIZE - 2
            )
            pygame.draw.rect(self.screen, color, rect, 2)
    
    def draw_path(self, path, offset_x, offset_y, color, width=3):
        """
        Draw the final path as a connected line.
        
        @param path: List of cells in path order
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param color: Path color
        @param width: Line width
        """
        if not path or len(path) < 2:
            return
        
        # Draw path cells with highlight
        for cell in path:
            rect = pygame.Rect(
                offset_x + cell.x * CELL_SIZE + 3,
                offset_y + cell.y * CELL_SIZE + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6
            )
            pygame.draw.rect(self.screen, color, rect, border_radius=2)
        
        # Draw connecting line
        points = []
        for cell in path:
            x = offset_x + cell.x * CELL_SIZE + CELL_SIZE // 2
            y = offset_y + cell.y * CELL_SIZE + CELL_SIZE // 2
            points.append((x, y))
        
        if len(points) >= 2:
            pygame.draw.lines(self.screen, color, False, points, width)
    
    def draw_current(self, cell, offset_x, offset_y, color):
        """
        Draw the currently expanding cell with glow effect.
        
        @param cell: Current cell
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param color: Highlight color
        """
        if cell is None:
            return
        
        center_x = offset_x + cell.x * CELL_SIZE + CELL_SIZE // 2
        center_y = offset_y + cell.y * CELL_SIZE + CELL_SIZE // 2
        
        # Outer glow
        pygame.draw.circle(self.screen, color, (center_x, center_y), CELL_SIZE // 2 + 2, 3)
        
        # Inner solid
        pygame.draw.circle(self.screen, color, (center_x, center_y), CELL_SIZE // 3)
    
    def add_particle(self, cell, offset_x, offset_y, color, side='A'):
        """
        Add a particle trail at a cell.
        
        @param cell: Cell location
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param color: Particle color
        @param side: 'A' or 'B' for which algorithm
        """
        x = offset_x + cell.x * CELL_SIZE + CELL_SIZE // 2
        y = offset_y + cell.y * CELL_SIZE + CELL_SIZE // 2
        
        particle = Particle(x, y, color)
        
        if side == 'A':
            self.particles_a.append(particle)
        else:
            self.particles_b.append(particle)
    
    def update_particles(self):
        """Update all particles and remove dead ones."""
        # Update and filter particles
        for particle in self.particles_a:
            particle.update()
        for particle in self.particles_b:
            particle.update()
        
        self.particles_a = [p for p in self.particles_a if not p.is_dead()]
        self.particles_b = [p for p in self.particles_b if not p.is_dead()]
    
    def draw_particles(self):
        """Draw all active particles."""
        for particle in self.particles_a:
            particle.draw(self.screen)
        for particle in self.particles_b:
            particle.draw(self.screen)
    
    def clear_particles(self):
        """Remove all particles."""
        self.particles_a.clear()
        self.particles_b.clear()
    
    def draw_heat_map(self, explored_counts, offset_x, offset_y, grid):
        """
        Draw a heat map showing exploration density.
        
        @param explored_counts: Dict mapping (x,y) to exploration count
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param grid: Grid for dimensions
        """
        if not explored_counts:
            return
        
        max_count = max(explored_counts.values()) if explored_counts else 1
        
        for (x, y), count in explored_counts.items():
            if count > 0:
                # Interpolate color from blue (cold) to red (hot)
                t = count / max_count
                r = int(lerp(0, 255, t))
                g = int(lerp(100, 50, t))
                b = int(lerp(255, 50, t))
                
                rect = pygame.Rect(
                    offset_x + x * CELL_SIZE + 2,
                    offset_y + y * CELL_SIZE + 2,
                    CELL_SIZE - 4,
                    CELL_SIZE - 4
                )
                
                overlay = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)
                overlay.fill((r, g, b, 150))
                self.screen.blit(overlay, (rect.x, rect.y))
    
    def _reconstruct_path_to_current(self, came_from, start, current):
        """
        Reconstruct path from start to current node.
        
        @param came_from: Dictionary mapping node to its parent
        @param start: Start cell
        @param current: Current cell
        @return: List of cells from start to current
        """
        if current is None or came_from is None:
            return []
        
        path = []
        node = current
        max_iterations = 10000  # Safety limit
        iterations = 0
        
        while node is not None and iterations < max_iterations:
            path.append(node)
            node = came_from.get(node)
            iterations += 1
        
        path.reverse()
        return path
    
    def draw_current_path(self, came_from, start, current, offset_x, offset_y, color, alpha=180):
        """
        Draw the path from start to current node during exploration.
        
        @param came_from: Parent pointer dictionary
        @param start: Start cell
        @param current: Current cell being explored
        @param offset_x: Grid X offset
        @param offset_y: Grid Y offset
        @param color: Path color
        @param alpha: Transparency
        """
        path = self._reconstruct_path_to_current(came_from, start, current)
        
        if not path or len(path) < 2:
            return
        
        # Draw path cells with semi-transparent overlay
        overlay = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4), pygame.SRCALPHA)
        overlay.fill((*color[:3], alpha))
        
        for cell in path:
            x = offset_x + cell.x * CELL_SIZE + 2
            y = offset_y + cell.y * CELL_SIZE + 2
            self.screen.blit(overlay, (x, y))
        
        # Draw connecting line
        points = []
        for cell in path:
            x = offset_x + cell.x * CELL_SIZE + CELL_SIZE // 2
            y = offset_y + cell.y * CELL_SIZE + CELL_SIZE // 2
            points.append((x, y))
        
        if len(points) >= 2:
            pygame.draw.lines(self.screen, color, False, points, 2)
    
    def draw_algorithm_race(self, grid, state_a, state_b, finished_a, finished_b):
        """
        Draw both algorithm visualizations for racing.
        
        @param grid: Shared grid
        @param state_a: Current state dict for algorithm A
        @param state_b: Current state dict for algorithm B
        @param finished_a: Whether A has finished
        @param finished_b: Whether B has finished
        """
        # Draw left grid (Algorithm A)
        self.draw_grid(grid, LEFT_GRID_X, GRID_Y)
        
        if state_a:
            explored_a = state_a.get('explored', set())
            self.draw_explored(explored_a, LEFT_GRID_X, GRID_Y, COLOR_A_EXPLORED[:3], 80)
            
            if finished_a and state_a.get('path'):
                # Final path - solid and prominent
                self.draw_path(state_a['path'], LEFT_GRID_X, GRID_Y, COLOR_A_PATH)
            else:
                # Show current path during exploration
                came_from = state_a.get('came_from', {})
                current = state_a.get('current')
                if current and came_from:
                    self.draw_current_path(
                        came_from, grid.start, current,
                        LEFT_GRID_X, GRID_Y, COLOR_A_PATH, 150
                    )
                if current:
                    self.draw_current(current, LEFT_GRID_X, GRID_Y, COLOR_A_CURRENT)
        
        # Draw right grid (Algorithm B)
        self.draw_grid(grid, RIGHT_GRID_X, GRID_Y)
        
        if state_b:
            explored_b = state_b.get('explored', set())
            self.draw_explored(explored_b, RIGHT_GRID_X, GRID_Y, COLOR_B_EXPLORED[:3], 80)
            
            if finished_b and state_b.get('path'):
                # Final path - solid and prominent
                self.draw_path(state_b['path'], RIGHT_GRID_X, GRID_Y, COLOR_B_PATH)
            else:
                # Show current path during exploration
                came_from = state_b.get('came_from', {})
                current = state_b.get('current')
                if current and came_from:
                    self.draw_current_path(
                        came_from, grid.start, current,
                        RIGHT_GRID_X, GRID_Y, COLOR_B_PATH, 150
                    )
                if current:
                    self.draw_current(current, RIGHT_GRID_X, GRID_Y, COLOR_B_CURRENT)
        
        # Draw particles
        self.draw_particles()
