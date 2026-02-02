"""
AI Pathfinding Racing Arena - Main Application

A visual educational tool demonstrating uninformed and informed search
algorithms through competitive split-screen racing.

Usage:
    python main.py

Controls:
    - Select algorithms from dropdowns
    - Click "Generate Maze" for new random maze
    - Click "Start Race" to begin competition
    - Use speed slider to control animation
    - Click "Reset" to stop and reset

@author: CPS 170 AI Course Project
"""

import pygame
import sys
import time
import asyncio

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, TITLE,
    GRID_WIDTH, GRID_HEIGHT, CELL_SIZE,
    COLOR_BG, COLOR_A_EXPLORED, COLOR_B_EXPLORED,
    LEFT_GRID_X, RIGHT_GRID_X, GRID_Y,
    SPEED_INSTANT
)
from grid import Grid
from maze_generator import generate_maze
from algorithms import ALGORITHMS, ALGORITHM_INFO
from visualizer import Visualizer
from ui import UI
from utils import calculate_path_cost


class RaceState:
    """
    Manages the state of a racing algorithm.
    
    Attributes:
        name: Algorithm name
        generator: Algorithm generator instance
        state: Current state dictionary from generator
        finished: Whether algorithm has completed
        start_time: When this algorithm started
        end_time: When this algorithm finished
    """
    
    def __init__(self, name, generator):
        """
        Initialize race state.
        
        @param name: Algorithm name
        @param generator: Algorithm generator function
        """
        self.name = name
        self.generator = generator
        self.state = None
        self.finished = False
        self.found_path = False
        self.start_time = 0
        self.end_time = 0
        self.path = None
        self.path_cost = 0
        self.nodes_explored = 0
    
    def step(self):
        """
        Execute one step of the algorithm.
        
        @return: True if step successful, False if finished
        """
        if self.finished:
            return False
        
        try:
            self.state = next(self.generator)
            
            if self.state.get('found'):
                self.finished = True
                self.found_path = True
                self.end_time = time.perf_counter()
                self.path = self.state.get('path', [])
                self.path_cost = self.state.get('path_cost', 0)
            
            explored = self.state.get('explored', set())
            self.nodes_explored = len(explored)
            
            return True
            
        except StopIteration:
            self.finished = True
            self.end_time = time.perf_counter()
            return False
    
    def get_time(self):
        """Get elapsed time."""
        if self.finished:
            return self.end_time - self.start_time
        elif self.start_time > 0:
            return time.perf_counter() - self.start_time
        return 0


class PathfindingArena:
    """
    Main application class for the pathfinding racing arena.
    
    Manages the game loop, event handling, and race coordination.
    """
    
    def __init__(self):
        """Initialize the application."""
        pygame.init()
        pygame.display.set_caption(TITLE)
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.visualizer = Visualizer(self.screen)
        self.ui = UI(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Initialize grid
        self.grid = None
        self.generate_new_maze()
        
        # Race state
        self.racing = False
        self.race_a = None
        self.race_b = None
        self.steps_per_frame = 1
        self.last_step_time = 0
        self.step_interval = 0
        
        # Running flag
        self.running = True
    
    def generate_new_maze(self):
        """Generate a new random maze."""
        self.grid = generate_maze(GRID_WIDTH, GRID_HEIGHT, maze_type="open")
        self.visualizer.clear_particles()
        self.ui.reset_stats()
    
    def start_race(self):
        """Start a new race between selected algorithms."""
        if self.racing:
            return
        
        algo_a, algo_b = self.ui.get_selected_algorithms()
        
        # Get algorithm generators
        gen_a_func = ALGORITHMS.get(algo_a)
        gen_b_func = ALGORITHMS.get(algo_b)
        
        if not gen_a_func or not gen_b_func:
            return
        
        # Create race states
        self.race_a = RaceState(algo_a, gen_a_func(self.grid))
        self.race_b = RaceState(algo_b, gen_b_func(self.grid))
        
        # Set start times
        start_time = time.perf_counter()
        self.race_a.start_time = start_time
        self.race_b.start_time = start_time
        
        # Update UI
        self.ui.update_stats_a(name=algo_a, status='Running')
        self.ui.update_stats_b(name=algo_b, status='Running')
        self.ui.set_racing(True)
        self.ui.winner_banner.hide()
        
        # Clear particles
        self.visualizer.clear_particles()
        
        # Set speed
        speed = self.ui.get_speed()
        if speed == SPEED_INSTANT:
            self.step_interval = 0
            self.steps_per_frame = 10000  # Run to completion
        else:
            self.step_interval = 1.0 / speed
            self.steps_per_frame = max(1, speed // FPS)
        
        self.racing = True
        self.last_step_time = time.perf_counter()
    
    def reset_race(self):
        """Reset the current race."""
        self.racing = False
        self.race_a = None
        self.race_b = None
        self.ui.set_racing(False)
        self.ui.reset_stats()
        self.visualizer.clear_particles()
    
    def step_race(self):
        """Execute race steps based on speed setting."""
        if not self.racing:
            return
        
        current_time = time.perf_counter()
        
        # Check if enough time has passed for next step
        if self.step_interval > 0:
            elapsed = current_time - self.last_step_time
            if elapsed < self.step_interval:
                return
            self.last_step_time = current_time
        
        # Execute steps
        for _ in range(self.steps_per_frame):
            stepped_a = False
            stepped_b = False
            
            if not self.race_a.finished:
                stepped_a = self.race_a.step()
                if stepped_a and self.race_a.state:
                    current = self.race_a.state.get('current')
                    if current:
                        self.visualizer.add_particle(
                            current, LEFT_GRID_X, GRID_Y,
                            COLOR_A_EXPLORED[:3], 'A'
                        )
            
            if not self.race_b.finished:
                stepped_b = self.race_b.step()
                if stepped_b and self.race_b.state:
                    current = self.race_b.state.get('current')
                    if current:
                        self.visualizer.add_particle(
                            current, RIGHT_GRID_X, GRID_Y,
                            COLOR_B_EXPLORED[:3], 'B'
                        )
            
            # Update stats
            self._update_race_stats()
            
            # Check if race is complete
            if self.race_a.finished and self.race_b.finished:
                self._finish_race()
                return
            
            # For instant mode, continue until done
            if self.step_interval == 0:
                continue
            else:
                break
    
    def _update_race_stats(self):
        """Update UI stats during race."""
        if self.race_a:
            self.ui.update_stats_a(
                nodes_explored=self.race_a.nodes_explored,
                path_length=len(self.race_a.path) if self.race_a.path else 0,
                path_cost=self.race_a.path_cost,
                time=self.race_a.get_time(),
                status='Complete' if self.race_a.finished else 'Running'
            )
        
        if self.race_b:
            self.ui.update_stats_b(
                nodes_explored=self.race_b.nodes_explored,
                path_length=len(self.race_b.path) if self.race_b.path else 0,
                path_cost=self.race_b.path_cost,
                time=self.race_b.get_time(),
                status='Complete' if self.race_b.finished else 'Running'
            )
    
    def _finish_race(self):
        """Handle race completion and determine winner."""
        self.racing = False
        self.ui.set_racing(False)
        
        # Determine winner
        a_found = self.race_a.found_path
        b_found = self.race_b.found_path
        
        if not a_found and not b_found:
            self.ui.winner_banner.show_no_path("Neither algorithm")
        elif not a_found:
            self.ui.winner_banner.show_winner(self.race_b.name, "A found no path")
        elif not b_found:
            self.ui.winner_banner.show_winner(self.race_a.name, "B found no path")
        else:
            # Both found paths - compare metrics
            a_cost = self.race_a.path_cost
            b_cost = self.race_b.path_cost
            a_nodes = self.race_a.nodes_explored
            b_nodes = self.race_b.nodes_explored
            
            if a_cost < b_cost:
                self.ui.winner_banner.show_winner(
                    self.race_a.name, 
                    f"Lower cost: {a_cost:.0f} vs {b_cost:.0f}"
                )
            elif b_cost < a_cost:
                self.ui.winner_banner.show_winner(
                    self.race_b.name,
                    f"Lower cost: {b_cost:.0f} vs {a_cost:.0f}"
                )
            elif a_nodes < b_nodes:
                self.ui.winner_banner.show_winner(
                    self.race_a.name,
                    f"Fewer nodes: {a_nodes} vs {b_nodes}"
                )
            elif b_nodes < a_nodes:
                self.ui.winner_banner.show_winner(
                    self.race_b.name,
                    f"Fewer nodes: {b_nodes} vs {a_nodes}"
                )
            else:
                self.ui.winner_banner.show_tie("Same cost and nodes explored")
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key == pygame.K_SPACE:
                    if self.racing:
                        self.reset_race()
                    else:
                        self.start_race()
                elif event.key == pygame.K_g:
                    if not self.racing:
                        self.generate_new_maze()
                elif event.key == pygame.K_r:
                    self.reset_race()
            
            # Handle UI events
            action = self.ui.handle_event(event)
            if action == "generate":
                if not self.racing:
                    self.generate_new_maze()
            elif action == "start":
                self.start_race()
            elif action == "reset":
                self.reset_race()
    
    def update(self):
        """Update game state."""
        # Step race if running
        self.step_race()
        
        # Update particles
        self.visualizer.update_particles()
    
    def render(self):
        """Render the frame."""
        # Clear screen
        self.screen.fill(COLOR_BG)
        
        # Draw grids
        if self.racing and self.race_a and self.race_b:
            self.visualizer.draw_algorithm_race(
                self.grid,
                self.race_a.state,
                self.race_b.state,
                self.race_a.finished,
                self.race_b.finished
            )
        else:
            # Draw static grids when not racing
            self.visualizer.draw_grid(self.grid, LEFT_GRID_X, GRID_Y)
            self.visualizer.draw_grid(self.grid, RIGHT_GRID_X, GRID_Y)
            
            # If race finished, draw final paths
            if self.race_a and self.race_a.finished and self.race_a.path:
                self.visualizer.draw_path(
                    self.race_a.path, LEFT_GRID_X, GRID_Y,
                    (30, 100, 255)
                )
            if self.race_b and self.race_b.finished and self.race_b.path:
                self.visualizer.draw_path(
                    self.race_b.path, RIGHT_GRID_X, GRID_Y,
                    (255, 60, 60)
                )
        
        # Draw particles
        self.visualizer.draw_particles()
        
        # Draw UI
        self.ui.draw()
        
        # Update display
        pygame.display.flip()
    
    async def run(self):
        """Main game loop (async for Pygbag web compatibility)."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
            await asyncio.sleep(0)  # Required for Pygbag
        
        pygame.quit()


async def main():
    """Application entry point (async for Pygbag)."""
    arena = PathfindingArena()
    await arena.run()


if __name__ == "__main__":
    asyncio.run(main())
