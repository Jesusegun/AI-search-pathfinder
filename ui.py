import pygame
from config import (
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_TEXT_HIGHLIGHT,
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_ACTIVE, COLOR_BUTTON_BORDER,
    COLOR_DROPDOWN_BG, COLOR_UI_BG, COLOR_PANEL_BG,
    COLOR_SUCCESS, COLOR_FAILURE, COLOR_WARNING,
    UNINFORMED_ALGORITHMS, INFORMED_ALGORITHMS, SPEED_OPTIONS,
    LEFT_GRID_X, RIGHT_GRID_X,
    STATS_Y, STATS_HEIGHT
)


class Button:
    def __init__(self, x, y, width, height, text, font_size=22):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hovered = False
        self.active = False
        self.enabled = True
        self.font = pygame.font.Font(None, font_size)
    
    def handle_event(self, event):
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
        if self.active:
            color = COLOR_BUTTON_ACTIVE
        elif self.hovered:
            color = COLOR_BUTTON_HOVER
        else:
            color = COLOR_BUTTON
        
        if not self.enabled:
            color = tuple(c // 2 for c in color)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.rect, 2, border_radius=5)
        
        text_color = COLOR_TEXT if self.enabled else COLOR_TEXT_DIM
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Dropdown:
    def __init__(self, x, y, width, height, options, default_index=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = default_index
        self.selected = options[default_index] if options else ""
        self.expanded = False
        self.hovered_index = -1
        self.font = pygame.font.Font(None, 22)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
                return False
            elif self.expanded:
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
        pygame.draw.rect(screen, COLOR_DROPDOWN_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.rect, 2, border_radius=5)
        
        text = self.font.render(self.selected, True, COLOR_TEXT)
        text_rect = text.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text, text_rect)
        
        arrow_x = self.rect.right - 20
        arrow_y = self.rect.centery
        if self.expanded:
            points = [(arrow_x - 5, arrow_y + 3), (arrow_x + 5, arrow_y + 3), (arrow_x, arrow_y - 4)]
        else:
            points = [(arrow_x - 5, arrow_y - 3), (arrow_x + 5, arrow_y - 3), (arrow_x, arrow_y + 4)]
        pygame.draw.polygon(screen, COLOR_TEXT, points)
        
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
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_index = 1  # Default to Normal
        self.dragging = False
        self.font = pygame.font.Font(None, 18)
    
    @property
    def value(self):
        return self.options[self.selected_index][1]
    
    @property
    def label(self):
        return self.options[self.selected_index][0]
    
    def handle_event(self, event):
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
        relative_x = mouse_x - self.rect.x
        step_width = self.rect.width / len(self.options)
        new_index = int(relative_x / step_width)
        new_index = max(0, min(new_index, len(self.options) - 1))
        
        if new_index != self.selected_index:
            self.selected_index = new_index
            return True
        return False
    
    def draw(self, screen):
        track_y = self.rect.centery
        pygame.draw.line(
            screen, COLOR_BUTTON_BORDER,
            (self.rect.x, track_y), (self.rect.right, track_y), 3
        )
        
        step_width = self.rect.width / (len(self.options) - 1)
        for i, (label, _) in enumerate(self.options):
            x = self.rect.x + int(i * step_width)
            
            pygame.draw.line(screen, COLOR_TEXT_DIM, (x, track_y - 5), (x, track_y + 5), 2)
            
            text = self.font.render(label, True, COLOR_TEXT_DIM)
            text_rect = text.get_rect(midtop=(x, track_y + 8))
            screen.blit(text, text_rect)
        
        handle_x = self.rect.x + int(self.selected_index * step_width)
        pygame.draw.circle(screen, COLOR_TEXT_HIGHLIGHT, (handle_x, track_y), 8)
        pygame.draw.circle(screen, COLOR_TEXT, (handle_x, track_y), 6)


class StatsPanel:
    def __init__(self, x, y, width, height, title="Algorithm"):
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
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] = value
    
    def reset(self):
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
        pygame.draw.rect(screen, COLOR_PANEL_BG, self.rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, self.rect, 2, border_radius=8)
        
        title_text = self.font_title.render(self.title, True, COLOR_TEXT_HIGHLIGHT)
        screen.blit(title_text, (self.rect.x + 15, self.rect.y + 10))
        
        name_text = self.font_title.render(self.stats['name'], True, COLOR_TEXT)
        screen.blit(name_text, (self.rect.x + 15, self.rect.y + 35))
        
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
        if seconds >= 1:
            return f"{seconds:.2f}s"
        else:
            return f"{seconds * 1000:.0f}ms"


class WinnerBanner:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 32)
        self.message = ""
        self.visible = False
        self.color = COLOR_SUCCESS
    
    def show_winner(self, winner_name, reason):
        self.message = f"WINNER: {winner_name} ({reason})"
        self.visible = True
        self.color = COLOR_SUCCESS
    
    def show_tie(self, reason):
        self.message = f"TIE: {reason}"
        self.visible = True
        self.color = COLOR_WARNING
    
    def show_no_path(self, algorithm_name):
        self.message = f"{algorithm_name}: No path found!"
        self.visible = True
        self.color = COLOR_FAILURE
    
    def hide(self):
        self.visible = False
        self.message = ""
    
    def draw(self, screen):
        if not self.visible:
            return
        
        pygame.draw.rect(screen, COLOR_PANEL_BG, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.color, self.rect, 3, border_radius=10)
        
        text = self.font.render(self.message, True, self.color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class UI:
    def __init__(self, screen, window_width, window_height):
        self.screen = screen
        self.width = window_width
        self.height = window_height
        
        self.font_title = pygame.font.Font(None, 32)
        self.font_label = pygame.font.Font(None, 18)
        
        btn_y = 52
        self.btn_generate = Button(280, btn_y, 130, 32, "Generate Maze", 20)
        self.btn_start = Button(420, btn_y, 110, 32, "Start Race", 20)
        self.btn_reset = Button(540, btn_y, 80, 32, "Reset", 20)
        
        self.dropdown_algo_a = Dropdown(130, btn_y, 100, 32, UNINFORMED_ALGORITHMS, 0)
        self.dropdown_algo_b = Dropdown(905, btn_y, 100, 32, INFORMED_ALGORITHMS, 1)
        
        self.slider_speed = Slider(650, btn_y + 2, 140, 28, SPEED_OPTIONS)
        
        panel_width = 250
        self.stats_a = StatsPanel(LEFT_GRID_X, STATS_Y, panel_width, STATS_HEIGHT, "Algorithm A")
        self.stats_b = StatsPanel(RIGHT_GRID_X, STATS_Y, panel_width, STATS_HEIGHT, "Algorithm B")
        
        banner_y = STATS_Y + STATS_HEIGHT + 8
        banner_width = 450
        banner_x = (window_width - banner_width) // 2
        self.winner_banner = WinnerBanner(banner_x, banner_y, banner_width, 40)
    
    def handle_event(self, event):
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
        return (self.dropdown_algo_a.selected, self.dropdown_algo_b.selected)
    
    def get_speed(self):
        return self.slider_speed.value
    
    def update_stats_a(self, **kwargs):
        self.stats_a.update(**kwargs)
    
    def update_stats_b(self, **kwargs):
        self.stats_b.update(**kwargs)
    
    def reset_stats(self):
        self.stats_a.reset()
        self.stats_b.reset()
        self.winner_banner.hide()
    
    def set_racing(self, racing):
        self.btn_generate.enabled = not racing
        self.btn_start.enabled = not racing
        self.btn_start.text = "Racing..." if racing else "Start Race"
    
    def draw(self):
        title = self.font_title.render("AI Pathfinding Racing Arena", True, COLOR_TEXT)
        title_rect = title.get_rect(centerx=self.width // 2, y=12)
        self.screen.blit(title, title_rect)
        
        dropdown_label_font = pygame.font.Font(None, 26)
        label_a = dropdown_label_font.render("Uninformed:", True, COLOR_TEXT_HIGHLIGHT)
        self.screen.blit(label_a, (20, 58))
        
        label_b = dropdown_label_font.render("Informed:", True, COLOR_TEXT_HIGHLIGHT)
        self.screen.blit(label_b, (820, 58))
        
        speed_label = self.font_label.render("Speed:", True, COLOR_TEXT_DIM)
        self.screen.blit(speed_label, (650, 38))
        
        self.btn_generate.draw(self.screen)
        self.btn_start.draw(self.screen)
        self.btn_reset.draw(self.screen)
        self.dropdown_algo_a.draw(self.screen)
        self.dropdown_algo_b.draw(self.screen)
        self.slider_speed.draw(self.screen)
        self.stats_a.draw(self.screen)
        self.stats_b.draw(self.screen)
        self.winner_banner.draw(self.screen)
