# AI Pathfinding Racing Arena

A visual educational tool demonstrating uninformed and informed search algorithms through competitive split-screen racing.

## Overview

This application allows you to compare how different pathfinding algorithms perform on the same maze. Two algorithms race simultaneously on identical mazes in a split-screen view, providing direct performance comparison.

## Features

- **6 Pathfinding Algorithms:**
  - **BFS** (Breadth-First Search) - Uninformed, explores by level
  - **DFS** (Depth-First Search) - Uninformed, explores depth first
  - **UCS** (Uniform Cost Search) - Uninformed, considers path cost
  - **Greedy** (Greedy Best-First) - Informed, uses heuristic only
  - **A*** (A* Search) - Informed, optimal with f = g + h
  - **IDA*** (Iterative Deepening A*) - Memory-efficient A*

- **Terrain System:**
  - **Floor** (white) - Cost: 1
  - **Mud** (brown) - Cost: 5
  - **Wall** (dark) - Impassable

- **Visualization:**
  - Split-screen racing
  - Particle trail effects
  - Real-time statistics
  - Winner declaration

## Installation

1. Ensure Python 3.8+ is installed

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

### Controls

| Control | Action |
|---------|--------|
| Algorithm Dropdowns | Select algorithms for left/right sides |
| Generate Maze | Create a new random maze |
| Start Race | Begin the race between selected algorithms |
| Reset | Stop current race and reset |
| Speed Slider | Adjust animation speed (Slow/Normal/Fast/Instant) |
| Space | Toggle Start/Reset |
| G | Generate new maze |
| R | Reset race |
| ESC | Exit application |

## Understanding the Results

### Key Metrics

- **Nodes Explored**: How many cells the algorithm examined
- **Path Length**: Number of steps in the final path
- **Path Cost**: Total cost considering terrain (floor=1, mud=5)
- **Time**: Execution time

### Algorithm Comparison

| Algorithm | Complete | Optimal | Best For |
|-----------|----------|---------|----------|
| BFS | ✓ | Steps only | Finding shortest path (steps) |
| DFS | ✗ | ✗ | Memory-constrained scenarios |
| UCS | ✓ | ✓ (cost) | Finding lowest-cost path |
| Greedy | ✗ | ✗ | Fast but potentially suboptimal |
| A* | ✓ | ✓ | Best overall performance |
| IDA* | ✓ | ✓ | Memory-efficient optimal search |

### Terrain Cost Demo

Try racing **BFS vs A*** on a maze with mud patches:
- BFS may plow through mud if that path has fewer steps
- A* intelligently routes around expensive terrain
- Compare the **Path Cost** to see the difference!

## Project Structure

```
pathfinding-arena/
├── main.py           # Application entry point
├── config.py         # Configuration constants
├── grid.py           # Grid and cell classes
├── maze_generator.py # Maze generation algorithms
├── algorithms.py     # All 6 pathfinding algorithms
├── visualizer.py     # Rendering and animation
├── ui.py             # User interface components
├── utils.py          # Helper functions
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Academic Context

This project demonstrates concepts from AI search algorithms:
- State space vs search tree
- Fringe/frontier management
- Heuristic functions (Manhattan distance)
- Completeness and optimality
- Time and space complexity

## License

MIT License - Educational use encouraged.
