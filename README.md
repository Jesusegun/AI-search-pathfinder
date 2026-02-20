# Pathfinding Algorithm Visualizer

A pygame app that lets you watch different pathfinding algorithms race against each other on the same maze.

## What it does

Pick two algorithms and watch them race side-by-side on identical mazes. You can see which one finds the path faster and which explores fewer nodes. It's pretty cool to see how algorithms like A* are way smarter than BFS when there's mud on the ground.

## Algorithms

Implemented 6 algorithms for the project:

**Uninformed Search:**
- BFS - explores level by level
- DFS - goes deep first
- UCS - picks lowest cost path

**Informed Search:**
- Greedy - rushes toward the goal (not always optimal)
- A* - the smart one, uses cost + heuristic
- IDA* - like A* but uses less memory

The maze has three terrain types: normal floor (cost 1), mud (cost 5), and walls. Some algorithms ignore terrain cost and just count steps, which can lead to bad paths.

## Installation

You need Python 3.8 or higher.

Install the required packages:
```bash
pip install -r requirements.txt
```

## How to run

```bash
python main.py
```

## Web build (PyBag) + GitHub Pages

This project uses `pygbag` to package the game for web and serves it from `docs/` (GitHub Pages).

Build and sync web files:

```bash
python build_web.py
```

Useful options:

- `python build_web.py --replace-index` to replace `docs/index.html` with the generated one.
- `python build_web.py --no-clean-docs` to skip stale-file cleanup in `docs/`.

Typical deploy flow:

1. Update your game code (for example `main.py`).
2. Run `python build_web.py`.
3. Commit source changes + `docs/` artifacts.
4. Push to `main`.
5. In GitHub Pages settings, use branch `main` and folder `/docs`.

## Controls

- Use the dropdowns to pick algorithms for each side
- "Generate Maze" makes a new random maze
- "Start Race" starts the race
- Speed slider controls how fast it runs (instant mode is useful for testing)
- Spacebar to start/reset
- G for new maze
- ESC to quit

## Interesting things to try

**BFS vs A* with mud:**
BFS doesn't care about terrain cost so it might walk through a bunch of mud if it's fewer steps. A* actually avoids the mud and finds a cheaper path. You can see this clearly in the "Path Cost" stat.

**Greedy vs A*:**
Greedy is fast but sometimes gets stuck or finds bad paths. A* is almost always better.

**DFS:**
DFS is interesting because it just picks a direction and goes. Sometimes it gets lucky, sometimes it explores way too much.

## Stats explained

- **Nodes Explored** - how many cells the algorithm looked at
- **Path Length** - number of steps in the final path  
- **Path Cost** - total cost (mud costs more)
- **Time** - how long it took

The winner is determined by lowest path cost. If costs are equal, then by fewest nodes explored.

## Files

```
main.py           - main entry point and game loop
config.py         - all the constants and colors
grid.py           - grid/cell classes
maze_generator.py - generates random mazes
algorithms.py     - all 6 search algorithms
visualizer.py     - draws everything
ui.py             - buttons, dropdowns, stats panels
utils.py          - helper functions (heuristics, path reconstruction)
```

## Notes

The algorithms are implemented as generators so they can yield their state at each step for visualization. This makes the racing animation possible.

For the course project, I focused on comparing uninformed vs informed search and showing how heuristics make a huge difference. A* consistently beats BFS/DFS on most mazes, especially with varied terrain costs.
