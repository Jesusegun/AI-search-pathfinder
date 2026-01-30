"""
Configuration constants for AI Pathfinding Racing Arena.

This module contains all configuration settings including:
- Window dimensions and FPS
- Grid settings and terrain types
- Color palette for all UI elements
- Speed presets and layout positions

@author: CPS 170 AI Course Project
"""

# =============================================================================
# WINDOW SETTINGS
# =============================================================================
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 620
FPS = 60
TITLE = "AI Pathfinding Racing Arena"

# =============================================================================
# GRID SETTINGS
# =============================================================================
GRID_WIDTH = 22
GRID_HEIGHT = 22
CELL_SIZE = 15

# =============================================================================
# TERRAIN TYPES
# =============================================================================
FLOOR = 0  # Walkable, low cost
MUD = 1    # Walkable, high cost
WALL = 2   # Impassable

# =============================================================================
# TERRAIN COSTS
# =============================================================================
COST_FLOOR = 1
COST_MUD = 5
COST_WALL = float('inf')

# =============================================================================
# MAZE GENERATION DEFAULTS
# =============================================================================
DEFAULT_WALL_PERCENT = 0.25
DEFAULT_MUD_PERCENT = 0.15

# =============================================================================
# COLOR PALETTE (RGB)
# =============================================================================

# Background colors
COLOR_BG = (15, 15, 25)
COLOR_UI_BG = (35, 35, 50)
COLOR_PANEL_BG = (25, 25, 40)

# Grid terrain colors
COLOR_FLOOR = (220, 220, 230)
COLOR_MUD = (139, 90, 43)
COLOR_WALL = (30, 30, 40)
COLOR_GRID_LINE = (80, 80, 100)

# Start and goal markers
COLOR_START = (0, 255, 120)
COLOR_GOAL = (255, 215, 0)

# Algorithm A (Left side - Blue theme)
COLOR_A_EXPLORED = (70, 130, 220, 180)
COLOR_A_PATH = (30, 100, 255)
COLOR_A_CURRENT = (0, 200, 255)
COLOR_A_FRONTIER = (100, 180, 255)

# Algorithm B (Right side - Red/Orange theme)
COLOR_B_EXPLORED = (220, 90, 90, 180)
COLOR_B_PATH = (255, 60, 60)
COLOR_B_CURRENT = (255, 150, 50)
COLOR_B_FRONTIER = (255, 120, 100)

# Text colors
COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_DIM = (150, 150, 160)
COLOR_TEXT_HIGHLIGHT = (100, 200, 255)

# Status colors
COLOR_SUCCESS = (50, 255, 120)
COLOR_FAILURE = (255, 80, 80)
COLOR_WARNING = (255, 200, 50)

# UI element colors - BRIGHT for visibility
COLOR_BUTTON = (70, 100, 160)
COLOR_BUTTON_HOVER = (90, 130, 200)
COLOR_BUTTON_ACTIVE = (110, 150, 220)
COLOR_BUTTON_BORDER = (150, 180, 255)
COLOR_DROPDOWN_BG = (60, 90, 140)

# =============================================================================
# SPEED SETTINGS (steps per second)
# =============================================================================
SPEED_SLOW = 15
SPEED_NORMAL = 40
SPEED_FAST = 120
SPEED_INSTANT = -1  # Complete immediately

SPEED_OPTIONS = [
    ("Slow", SPEED_SLOW),
    ("Normal", SPEED_NORMAL),
    ("Fast", SPEED_FAST),
    ("Instant", SPEED_INSTANT)
]

# =============================================================================
# LAYOUT POSITIONS
# =============================================================================
HEADER_Y = 15
CONTROLS_Y = 55

# Left grid (Algorithm A)
LEFT_GRID_X = 20
GRID_Y = 100

# Right grid (Algorithm B)
RIGHT_GRID_X = 530

# Stats panels
STATS_Y = GRID_Y + (GRID_HEIGHT * CELL_SIZE) + 10
STATS_HEIGHT = 100
LEFT_STATS_X = LEFT_GRID_X
RIGHT_STATS_X = RIGHT_GRID_X

# =============================================================================
# PARTICLE SETTINGS
# =============================================================================
PARTICLE_LIFETIME = 45  # frames
PARTICLE_SIZE = 4

# =============================================================================
# ALGORITHM NAMES
# =============================================================================
ALGORITHM_NAMES = [
    "BFS",
    "DFS", 
    "UCS",
    "Greedy",
    "A*",
    "IDA*"
]

# Algorithm descriptions for display
ALGORITHM_DESCRIPTIONS = {
    "BFS": "Breadth-First Search - Explores by level, FIFO queue",
    "DFS": "Depth-First Search - Goes deep first, LIFO stack",
    "UCS": "Uniform Cost Search - Expands lowest cost path",
    "Greedy": "Greedy Best-First - Rushes toward goal (h only)",
    "A*": "A* Search - Optimal with f = g + h",
    "IDA*": "Iterative Deepening A* - Memory-efficient A*"
}
