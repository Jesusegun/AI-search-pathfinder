"""
User interface components for the pathfinding racing arena.

This module provides:
- Button: Clickable buttons with hover effects
- Dropdown: Algorithm selection dropdown menus
- Slider: Speed control slider
- StatsPanel: Real-time algorithm statistics display
- UI: Main UI orchestrator class

@author: CPS 170 AI Course Project
"""

import pygame
from config import (
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_HIGHLIGHT,
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_ACTIVE, COLOR_BUTTON_BORDER,
    COLOR_DROPDOWN_BG, COLOR_UI_BG, COLOR_PANEL_BG,
    COLOR_SUCCESS, COLOR_FAILURE, COLOR_WARNING,
    ALGORITHM_NAMES, SPEED_OPTIONS,
    LEFT_GRID_X, RIGHT_GRID_X,
    STATS_Y, STATS_HEIGHT
)


class Button:
    """
    Clickable button with hover effects.
    
    Attributes:
        rect: Button rectangle
        text: Button label
        hovered: Mouse is over button
        active: Button is pressed
    """
    
    def __init__(self, x, y, width, height, text, font_size=22):
        """
        Initialize a button.
        
        @param x: X position
        @param y: Y position
        @param width: Button width
        @param height: Button height
        @param text: Button label
        @param font_size: Font size for label
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False
        self.active = False
        self.enabled = True
        self.font = pygame.font.Font(None, font_size)
    
    def handle_event(self, event):
        """
        Handle pygame event.
        
        @param event: Pygame event
        @return: True if button was clicked
        """
        if not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.active:
                self.active = False
                if self.hovered:
                    return True
        
        return False
    
    def draw(self, screen):
        """
        Draw the button.
        
        @param screen: Pygame surface to draw on
        """
        if self.active:
            color = COLOR_BUTTON_ACTIVE
        elif self.hovered:
            color = COLOR_BUTTON_HOVER
        else:
            color = COLOR_BUTTON
        
        if not self.enabled:
            color = tuple(c // 2 for c in color)
        
        # Draw button background
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.rect, 2, border_radius=5)
        
        # Draw text
        text_color = COLOR_TEXT if self.enabled else COLOR_TEXT_DIM
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Dropdown:
    """
    Dropdown menu for algorithm selection.
    
    Attributes:
        rect: Main button rectangle
        options: List of option strings
        selected: Currently selected option
        expanded: Whether dropdown is open
    """
    
    def __init__(self, x, y, width, height, options, default_index=0):
        """
        Initialize a dropdown.
        
        @param x: X position
        @param y: Y position
        @param width: Dropdown width
        @param height: Button height
        @param options: List of option strings
        @param default_index: Index of default selection
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.selected = options[default_index] if options else ""
        self.expanded = False
        self.hovered_index = -1
        self.font = pygame.font.Font(None, 22)
    
    def handle_event(self, event):
        """
        Handle pygame event.
        
        @param event: Pygame event
        @return: True if selection changed
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return False
            elif self.expanded:
                # Check if clicked on an option
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.bottom + i * self.rect.height,
                        self.rect.width,
                        self.rect.height
                    )
                    if option_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.selected = option
                        self.expanded = False
                        return True
                
                # Clicked outside, close dropdown
                self.expanded = False
        
        elif event.type == pygame.MOUSEMOTION:
            self.hovered_index = -1
            if self.expanded:
                for i in range(len(self.options)):
                    option_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.bottom + i * self.rect.height,
                        self.rect.width,
                        self.rect.height
                    )
                    if option_rect.collidepoint(event.pos):
                        self.hovered_index = i
                        break
        
        return False
    
    def draw(self, screen):
        """
        Draw the dropdown.
        
        @param screen: Pygame surface to draw on
        """
        # Draw main button
        pygame.draw.rect(screen, COLOR_DROPDOWN_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.rect, 2, border_radius=5)
        
        # Draw selected text
        text = self.font.render(self.selected, True, COLOR_TEXT)
        text_rect = text.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text, text_rect)
        
        # Draw dropdown arrow
        arrow_x = self.rect.right - 20
        arrow_y = self.rect.centery
        if self.expanded:
            points = [(arrow_x - 5, arrow_y + 3), (arrow_x + 5, arrow_y + 3), (arrow_x, arrow_y - 4)]
        else:
            points = [(arrow_x - 5, arrow_y - 3), (arrow_x + 5, arrow_y - 3), (arrow_x, arrow_y + 4)]
        pygame.draw.polygon(screen, COLOR_TEXT, points)
        
        # Draw expanded options
        if self.expanded:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.bottom + i * self.rect.height,
                    self.rect.width,
                    self.rect.height
                )
                
                bg_color = COLOR_BUTTON_HOVER if i == self.hovered_index else COLOR_DROPDOWN_BG
                pygame.draw.rect(screen, bg_color, option_rect)
                pygame.draw.rect(screen, COLOR_BUTTON_BORDER, option_rect, 1)
                
                text = self.font.render(option, True, COLOR_TEXT)
                text_rect = text.get_rect(midleft=(option_rect.x + 10, option_rect.centery))
                screen.blit(text, text_rect)


class Slider:
    """
    Speed control slider.
    
    Attributes:
        rect: Slider track rectangle
        handle_pos: Current handle position (0.0 to 1.0)
        options: List of (label, value) tuples
        selected_index: Currently selected option index
    """
    
    def __init__(self, x, y, width, height, options):
        """
        Initialize a slider.
        
        @param x: X position
        @param y: Y position
        @param width: Slider width
        @param height: Slider height
        @param options: List of (label, value) tuples
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = 1  # Default to Normal
        self.dragging = False
        self.font = pygame.font.Font(None, 18)
    
    @property
    def value(self):
        """Get current value."""
        return self.options[self.selected_index][1]
    
    @property
    def label(self):
        """Get current label."""
        return self.options[self.selected_index][0]
    
    def handle_event(self, event):
        """
        Handle pygame event.
        
        @param event: Pygame event
        @return: True if value changed
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return self._update_from_mouse(event.pos[0])
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            return self._update_from_mouse(event.pos[0])
        
        return False
    
    def _update_from_mouse(self, mouse_x):
        """
        Update selection based on mouse X position.
        
        @param mouse_x: Mouse X coordinate
        @return: True if selection changed
        """
        relative_x = mouse_x - self.rect.x
        step_width = self.rect.width / len(self.options)
        new_index = int(relative_x / step_width)
        new_index = max(0, min(new_index, len(self.options) - 1))
        
        if new_index != self.selected_index:
            self.selected_index = new_index
            return True
        return False
    
    def draw(self, screen):
        """
        Draw the slider.
        
        @param screen: Pygame surface to draw on
        """
        # Draw track
        track_y = self.rect.centery
        pygame.draw.line(
            screen, COLOR_BUTTON_BORDER,
            (self.rect.x, track_y), (self.rect.right, track_y), 3
        )
        
        # Draw tick marks and labels
        step_width = self.rect.width / (len(self.options) - 1)
        for i, (label, _) in enumerate(self.options):
            x = self.rect.x + int(i * step_width)
            
            # Tick mark
            pygame.draw.line(screen, COLOR_TEXT_DIM, (x, track_y - 5), (x, track_y + 5), 2)
            
            # Label
            text = self.font.render(label, True, COLOR_TEXT_DIM)
            text_rect = text.get_rect(midtop=(x, track_y + 8))
            screen.blit(text, text_rect)
        
        # Draw handle
        handle_x = self.rect.x + int(self.selected_index * step_width)
        pygame.draw.circle(screen, COLOR_TEXT_HIGHLIGHT, (handle_x, track_y), 8)
        pygame.draw.circle(screen, COLOR_TEXT, (handle_x, track_y), 6)


class StatsPanel:
    """
    Panel displaying algorithm statistics.
    
    Shows: name, nodes explored, path length, cost, time, status.
    """
    
    def __init__(self, x, y, width, height, title="Algorithm"):
        """
        Initialize a stats panel.
        
        @param x: X position
        @param y: Y position
        @param width: Panel width
        @param height: Panel height
        @param title: Panel title
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.font_title = pygame.font.Font(None, 26)
        self.font_stats = pygame.font.Font(None, 20)
        
        self.stats = {
            'name': '-',
            'nodes_explored': 0,
            'path_length': 0,
            'path_cost': 0,
            'time': 0.0,
            'status': 'Ready',
            'frontier_size': 0
        }
    
    def update(self, **kwargs):
        """
        Update statistics.
        
        @param kwargs: Statistics to update
        """
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] = value
    
    def reset(self):
        """Reset all statistics."""
        self.stats = {
            'name': '-',
            'nodes_explored': 0,
            'path_length': 0,
            'path_cost': 0,
            'time': 0.0,
            'status': 'Ready',
            'frontier_size': 0
        }
    
    def draw(self, screen):
        """
        Draw the stats panel.
        
        @param screen: Pygame surface to draw on
        """
        # Draw background
        pygame.draw.rect(screen, COLOR_PANEL_BG, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.rect, 2, border_radius=8)
        
        # Draw title
        title_text = self.font_title.render(self.title, True, COLOR_TEXT_HIGHLIGHT)
        screen.blit(title_text, (self.rect.x + 15, self.rect.y + 10))
        
        # Draw algorithm name
        name_text = self.font_title.render(self.stats['name'], True, COLOR_TEXT)
        screen.blit(name_text, (self.rect.x + 15, self.rect.y + 35))
        
        # Draw stats in two columns
        col1_x = self.rect.x + 15
        col2_x = self.rect.x + self.rect.width // 2
        row_y = self.rect.y + 65
        row_height = 22
        
        stats_display = [
            (f"Nodes: {self.stats['nodes_explored']:,}", col1_x),
            (f"Path Length: {self.stats['path_length']}", col2_x),
            (f"Path Cost: {self.stats['path_cost']:.1f}", col1_x),
            (f"Time: {self._format_time(self.stats['time'])}", col2_x),
        ]
        
        for i, (text, x) in enumerate(stats_display):
            y = row_y + (i // 2) * row_height
            text_surface = self.font_stats.render(text, True, COLOR_TEXT)
            screen.blit(text_surface, (x, y))
        
        # Draw status
        status = self.stats['status']
        if status == 'Complete':
            status_color = COLOR_SUCCESS
        elif status == 'Running':
            status_color = COLOR_WARNING
        elif status == 'Failed':
            status_color = COLOR_FAILURE
        else:
            status_color = COLOR_TEXT_DIM
        
        status_text = self.font_stats.render(f"Status: {status}", True, status_color)
        screen.blit(status_text, (col1_x, row_y + row_height * 2))
    
    def _format_time(self, seconds):
        """Format time for display."""
        if seconds >= 1:
            return f"{seconds:.2f}s"
        else:
            return f"{seconds * 1000:.0f}ms"


class WinnerBanner:
    """
    Banner displaying race winner.
    """
    
    def __init__(self, x, y, width, height):
        """Initialize winner banner."""
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 32)
        self.message = ""
        self.visible = False
        self.color = COLOR_SUCCESS
    
    def show_winner(self, winner_name, reason):
        """
        Show winner announcement.
        
        @param winner_name: Name of winning algorithm
        @param reason: Reason for winning
        """
        self.message = f"🏆 WINNER: {winner_name} ({reason})"
        self.visible = True
        self.color = COLOR_SUCCESS
    
    def show_tie(self, reason):
        """Show tie announcement."""
        self.message = f"🤝 TIE: {reason}"
        self.visible = True
        self.color = COLOR_WARNING
    
    def show_no_path(self, algorithm_name):
        """Show no path found message."""
        self.message = f"❌ {algorithm_name}: No path found!"
        self.visible = True
        self.color = COLOR_FAILURE
    
    def hide(self):
        """Hide the banner."""
        self.visible = False
        self.message = ""
    
    def draw(self, screen):
        """Draw the banner if visible."""
        if not self.visible:
            return
        
        # Draw background
        pygame.draw.rect(screen, COLOR_PANEL_BG, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.color, self.rect, 3, border_radius=10)
        
        # Draw message
        text = self.font.render(self.message, True, self.color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class UI:
    """
    Main UI orchestrator class.
    
    Manages all UI elements and their interactions.
    """
    
    def __init__(self, screen, window_width, window_height):
        """
        Initialize the UI.
        
        @param screen: Pygame display surface
        @param window_width: Window width
        @param window_height: Window height
        """
        self.screen = screen
        self.width = window_width
        self.height = window_height
        
        # Title font
        self.font_title = pygame.font.Font(None, 32)
        self.font_label = pygame.font.Font(None, 18)
        
        # Create buttons - centered in middle of screen
        btn_y = 52
        self.btn_generate = Button(280, btn_y, 130, 32, "Generate Maze", 20)
        self.btn_start = Button(420, btn_y, 110, 32, "Start Race", 20)
        self.btn_reset = Button(540, btn_y, 80, 32, "Reset", 20)
        
        # Create dropdowns - on left and right sides
        self.dropdown_algo_a = Dropdown(20, btn_y, 100, 32, ALGORITHM_NAMES, 0)  # BFS
        self.dropdown_algo_b = Dropdown(905, btn_y, 100, 32, ALGORITHM_NAMES, 4)  # A*
        
        # Create speed slider - between buttons and right dropdown
        self.slider_speed = Slider(650, btn_y + 2, 140, 28, SPEED_OPTIONS)
        
        # Create stats panels
        panel_width = 250
        self.stats_a = StatsPanel(LEFT_GRID_X, STATS_Y, panel_width, STATS_HEIGHT, "Algorithm A")
        self.stats_b = StatsPanel(RIGHT_GRID_X, STATS_Y, panel_width, STATS_HEIGHT, "Algorithm B")
        
        # Winner banner
        banner_y = STATS_Y + STATS_HEIGHT + 8
        banner_width = 450
        banner_x = (window_width - banner_width) // 2
        self.winner_banner = WinnerBanner(banner_x, banner_y, banner_width, 40)
    
    def handle_event(self, event):
        """
        Handle pygame event.
        
        @param event: Pygame event
        @return: Action string or None
        """
        if self.btn_generate.handle_event(event):
            return "generate"
        if self.btn_start.handle_event(event):
            return "start"
        if self.btn_reset.handle_event(event):
            return "reset"
        
        self.dropdown_algo_a.handle_event(event)
        self.dropdown_algo_b.handle_event(event)
        self.slider_speed.handle_event(event)
        
        return None
    
    def get_selected_algorithms(self):
        """
        Get currently selected algorithms.
        
        @return: Tuple of (algorithm_a_name, algorithm_b_name)
        """
        return (self.dropdown_algo_a.selected, self.dropdown_algo_b.selected)
    
    def get_speed(self):
        """
        Get current speed setting.
        
        @return: Steps per second (-1 for instant)
        """
        return self.slider_speed.value
    
    def update_stats_a(self, **kwargs):
        """Update algorithm A stats."""
        self.stats_a.update(**kwargs)
    
    def update_stats_b(self, **kwargs):
        """Update algorithm B stats."""
        self.stats_b.update(**kwargs)
    
    def reset_stats(self):
        """Reset both stats panels."""
        self.stats_a.reset()
        self.stats_b.reset()
        self.winner_banner.hide()
    
    def set_racing(self, racing):
        """
        Set racing state (disables/enables buttons).
        
        @param racing: Whether race is in progress
        """
        self.btn_generate.enabled = not racing
        self.btn_start.enabled = not racing
        self.btn_start.text = "Racing..." if racing else "Start Race"
    
    def draw(self):
        """Draw all UI elements."""
        # Draw title
        title = self.font_title.render("AI Pathfinding Racing Arena", True, COLOR_TEXT)
        title_rect = title.get_rect(centerx=self.width // 2, y=12)
        self.screen.blit(title, title_rect)
        
        # Draw labels for dropdowns
        label_a = self.font_label.render("Algorithm A:", True, COLOR_TEXT_DIM)
        self.screen.blit(label_a, (20, 38))
        
        label_b = self.font_label.render("Algorithm B:", True, COLOR_TEXT_DIM)
        self.screen.blit(label_b, (905, 38))
        
        # Draw speed label
        speed_label = self.font_label.render("Speed:", True, COLOR_TEXT_DIM)
        self.screen.blit(speed_label, (650, 38))
        
        # Draw all elements
        self.btn_generate.draw(self.screen)
        self.btn_start.draw(self.screen)
        self.btn_reset.draw(self.screen)
        self.dropdown_algo_a.draw(self.screen)
        self.dropdown_algo_b.draw(self.screen)
        self.slider_speed.draw(self.screen)
        self.stats_a.draw(self.screen)
        self.stats_b.draw(self.screen)
        self.winner_banner.draw(self.screen)
