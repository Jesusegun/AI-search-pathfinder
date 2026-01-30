"""
Pathfinding algorithms for the racing arena.

This module implements 6 search algorithms as generators for step-by-step
visualization during racing:

Uninformed (Blind) Search:
- BFS: Breadth-First Search (FIFO queue)
- DFS: Depth-First Search (LIFO stack)
- UCS: Uniform Cost Search (priority queue by g)

Informed (Heuristic) Search:
- Greedy: Greedy Best-First Search (priority by h)
- A*: A* Search (priority by f = g + h)
- IDA*: Iterative Deepening A* (depth-limited with f cutoff)

Each algorithm yields state dictionaries for visualization:
{
    'current': Current cell being expanded,
    'frontier': List of cells in frontier/fringe,
    'explored': Set of explored cells,
    'came_from': Parent pointer dictionary,
    'g_scores': Cost-to-reach dictionary (if applicable),
    'found': Boolean indicating if goal found,
    'path': Final path (when found),
    'iteration': Step number
}

@author: CPS 170 AI Course Project
"""

from collections import deque
import heapq
import time

from utils import heuristic, reconstruct_path, calculate_path_cost


class AlgorithmResult:
    """
    Container for algorithm execution results.
    
    Attributes:
        path: List of cells from start to goal
        explored: Set of all explored cells
        frontier_max: Maximum frontier size during execution
        nodes_explored: Total number of nodes expanded
        path_cost: Total cost of the path
        time_taken: Execution time in seconds
        found: Whether a path was found
        algorithm_name: Name of the algorithm
    """
    
    def __init__(self, algorithm_name):
        """Initialize result container."""
        self.algorithm_name = algorithm_name
        self.path = []
        self.explored = set()
        self.frontier_max = 0
        self.nodes_explored = 0
        self.path_cost = 0
        self.time_taken = 0
        self.found = False
        self.iterations = 0


# =============================================================================
# UNINFORMED SEARCH ALGORITHMS
# =============================================================================

def bfs_generator(grid):
    """
    Breadth-First Search generator.
    
    Explores nodes in FIFO order (level by level).
    Complete: YES
    Optimal: YES (for uniform cost)
    Time: O(b^d)
    Space: O(b^d)
    
    @param grid: Grid object with start and goal
    @yields: State dictionary for visualization
    """
    start = grid.start
    goal = grid.goal
    
    frontier = deque([start])
    came_from = {start: None}
    explored = set()
    iteration = 0
    
    while frontier:
        current = frontier.popleft()
        
        # Skip if already explored (handles duplicates in frontier)
        if current in explored:
            continue
        
        explored.add(current)
        iteration += 1
        
        # Yield state for visualization
        yield {
            'current': current,
            'frontier': list(frontier),
            'explored': explored.copy(),
            'came_from': came_from,
            'found': False,
            'path': None,
            'iteration': iteration,
            'frontier_size': len(frontier)
        }
        
        # Goal check
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield {
                'current': current,
                'frontier': list(frontier),
                'explored': explored.copy(),
                'came_from': came_from,
                'found': True,
                'path': path,
                'iteration': iteration,
                'frontier_size': len(frontier),
                'path_cost': calculate_path_cost(path, grid)
            }
            return
        
        # Expand neighbors
        for neighbor in grid.get_neighbors(current):
            if neighbor not in came_from:
                came_from[neighbor] = current
                frontier.append(neighbor)
    
    # No path found
    yield {
        'current': None,
        'frontier': [],
        'explored': explored.copy(),
        'came_from': came_from,
        'found': False,
        'path': None,
        'iteration': iteration,
        'frontier_size': 0
    }


def dfs_generator(grid):
    """
    Depth-First Search generator.
    
    Explores deepest nodes first using LIFO stack.
    Complete: NO (can loop infinitely)
    Optimal: NO
    Time: O(b^m)
    Space: O(bm) - much better than BFS
    
    @param grid: Grid object with start and goal
    @yields: State dictionary for visualization
    """
    start = grid.start
    goal = grid.goal
    
    frontier = [start]  # LIFO stack
    came_from = {start: None}
    explored = set()
    iteration = 0
    
    while frontier:
        current = frontier.pop()  # Pop from end (LIFO)
        
        if current in explored:
            continue
        
        explored.add(current)
        iteration += 1
        
        yield {
            'current': current,
            'frontier': list(frontier),
            'explored': explored.copy(),
            'came_from': came_from,
            'found': False,
            'path': None,
            'iteration': iteration,
            'frontier_size': len(frontier)
        }
        
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield {
                'current': current,
                'frontier': list(frontier),
                'explored': explored.copy(),
                'came_from': came_from,
                'found': True,
                'path': path,
                'iteration': iteration,
                'frontier_size': len(frontier),
                'path_cost': calculate_path_cost(path, grid)
            }
            return
        
        # Add neighbors in reverse order so first direction is explored first
        neighbors = grid.get_neighbors(current)
        for neighbor in reversed(neighbors):
            if neighbor not in explored and neighbor not in came_from:
                came_from[neighbor] = current
                frontier.append(neighbor)
    
    yield {
        'current': None,
        'frontier': [],
        'explored': explored.copy(),
        'came_from': came_from,
        'found': False,
        'path': None,
        'iteration': iteration,
        'frontier_size': 0
    }


def ucs_generator(grid):
    """
    Uniform Cost Search generator.
    
    Expands node with lowest path cost g(n).
    Complete: YES
    Optimal: YES (finds lowest-cost path)
    Time: O(b^(C*/ε))
    Space: O(b^(C*/ε))
    
    @param grid: Grid object with start and goal
    @yields: State dictionary for visualization
    """
    start = grid.start
    goal = grid.goal
    
    # Priority queue: (cost, tie-breaker, node)
    counter = 0
    frontier = [(0, counter, start)]
    came_from = {start: None}
    g_scores = {start: 0}
    explored = set()
    iteration = 0
    
    while frontier:
        current_cost, _, current = heapq.heappop(frontier)
        
        if current in explored:
            continue
        
        explored.add(current)
        iteration += 1
        
        yield {
            'current': current,
            'frontier': [(cost, node) for cost, _, node in frontier],
            'explored': explored.copy(),
            'came_from': came_from,
            'g_scores': g_scores.copy(),
            'found': False,
            'path': None,
            'iteration': iteration,
            'frontier_size': len(frontier),
            'current_cost': current_cost
        }
        
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield {
                'current': current,
                'frontier': [(cost, node) for cost, _, node in frontier],
                'explored': explored.copy(),
                'came_from': came_from,
                'g_scores': g_scores.copy(),
                'found': True,
                'path': path,
                'iteration': iteration,
                'frontier_size': len(frontier),
                'path_cost': g_scores[goal]
            }
            return
        
        for neighbor in grid.get_neighbors(current):
            new_cost = g_scores[current] + grid.get_cost(current, neighbor)
            
            if neighbor not in g_scores or new_cost < g_scores[neighbor]:
                g_scores[neighbor] = new_cost
                came_from[neighbor] = current
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, neighbor))
    
    yield {
        'current': None,
        'frontier': [],
        'explored': explored.copy(),
        'came_from': came_from,
        'g_scores': g_scores.copy(),
        'found': False,
        'path': None,
        'iteration': iteration,
        'frontier_size': 0
    }


# =============================================================================
# INFORMED SEARCH ALGORITHMS
# =============================================================================

def greedy_generator(grid):
    """
    Greedy Best-First Search generator.
    
    Expands node that appears closest to goal (h only).
    Complete: NO (can get stuck)
    Optimal: NO (ignores path cost)
    Fast but risky.
    
    @param grid: Grid object with start and goal
    @yields: State dictionary for visualization
    """
    start = grid.start
    goal = grid.goal
    
    counter = 0
    h_start = heuristic(start, goal)
    frontier = [(h_start, counter, start)]
    came_from = {start: None}
    explored = set()
    iteration = 0
    
    while frontier:
        h_value, _, current = heapq.heappop(frontier)
        
        if current in explored:
            continue
        
        explored.add(current)
        iteration += 1
        
        yield {
            'current': current,
            'frontier': [(h, node) for h, _, node in frontier],
            'explored': explored.copy(),
            'came_from': came_from,
            'found': False,
            'path': None,
            'iteration': iteration,
            'frontier_size': len(frontier),
            'h_value': h_value
        }
        
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield {
                'current': current,
                'frontier': [(h, node) for h, _, node in frontier],
                'explored': explored.copy(),
                'came_from': came_from,
                'found': True,
                'path': path,
                'iteration': iteration,
                'frontier_size': len(frontier),
                'path_cost': calculate_path_cost(path, grid)
            }
            return
        
        for neighbor in grid.get_neighbors(current):
            if neighbor not in explored and neighbor not in came_from:
                h = heuristic(neighbor, goal)
                came_from[neighbor] = current
                counter += 1
                heapq.heappush(frontier, (h, counter, neighbor))
    
    yield {
        'current': None,
        'frontier': [],
        'explored': explored.copy(),
        'came_from': came_from,
        'found': False,
        'path': None,
        'iteration': iteration,
        'frontier_size': 0
    }


def astar_generator(grid):
    """
    A* Search generator.
    
    Expands node with lowest f(n) = g(n) + h(n).
    Complete: YES
    Optimal: YES (with admissible heuristic)
    The gold standard of informed search.
    
    @param grid: Grid object with start and goal
    @yields: State dictionary for visualization
    """
    start = grid.start
    goal = grid.goal
    
    counter = 0
    h_start = heuristic(start, goal)
    frontier = [(h_start, counter, start)]  # f = g + h, initially g=0
    came_from = {start: None}
    g_scores = {start: 0}
    explored = set()
    iteration = 0
    
    while frontier:
        f_value, _, current = heapq.heappop(frontier)
        
        if current in explored:
            continue
        
        explored.add(current)
        iteration += 1
        
        g_current = g_scores[current]
        h_current = heuristic(current, goal)
        
        yield {
            'current': current,
            'frontier': [(f, node) for f, _, node in frontier],
            'explored': explored.copy(),
            'came_from': came_from,
            'g_scores': g_scores.copy(),
            'found': False,
            'path': None,
            'iteration': iteration,
            'frontier_size': len(frontier),
            'f_value': f_value,
            'g_value': g_current,
            'h_value': h_current
        }
        
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            yield {
                'current': current,
                'frontier': [(f, node) for f, _, node in frontier],
                'explored': explored.copy(),
                'came_from': came_from,
                'g_scores': g_scores.copy(),
                'found': True,
                'path': path,
                'iteration': iteration,
                'frontier_size': len(frontier),
                'path_cost': g_scores[goal]
            }
            return
        
        for neighbor in grid.get_neighbors(current):
            tentative_g = g_scores[current] + grid.get_cost(current, neighbor)
            
            if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                g_scores[neighbor] = tentative_g
                came_from[neighbor] = current
                f = tentative_g + heuristic(neighbor, goal)
                counter += 1
                heapq.heappush(frontier, (f, counter, neighbor))
    
    yield {
        'current': None,
        'frontier': [],
        'explored': explored.copy(),
        'came_from': came_from,
        'g_scores': g_scores.copy(),
        'found': False,
        'path': None,
        'iteration': iteration,
        'frontier_size': 0
    }


def idastar_generator(grid):
    """
    Iterative Deepening A* generator.
    
    Memory-efficient variant of A*.
    Uses depth-limited search with f-cost cutoff.
    Complete: YES
    Optimal: YES
    Space: O(d) - LINEAR!
    
    @param grid: Grid object with start and goal
    @yields: State dictionary for visualization
    """
    start = grid.start
    goal = grid.goal
    
    threshold = heuristic(start, goal)
    explored_total = set()
    iteration = 0
    ida_iteration = 0  # Which threshold iteration
    
    while True:
        ida_iteration += 1
        
        # Run depth-limited search with current threshold
        result_gen = _ida_search(
            grid, [start], 0, threshold, goal,
            explored_total, iteration
        )
        
        min_exceeded = float('inf')
        found = False
        final_path = None
        final_cost = 0
        
        for state in result_gen:
            iteration = state.get('iteration', iteration)
            explored_total = state.get('explored', explored_total)
            
            yield {
                'current': state.get('current'),
                'frontier': [],  # IDA* doesn't maintain explicit frontier
                'explored': explored_total.copy(),
                'came_from': {},
                'found': state.get('found', False),
                'path': state.get('path'),
                'iteration': iteration,
                'frontier_size': 0,
                'threshold': threshold,
                'ida_iteration': ida_iteration
            }
            
            if state.get('found'):
                found = True
                final_path = state.get('path')
                final_cost = state.get('path_cost', 0)
                break
            
            if state.get('exceeded'):
                exceeded_val = state.get('exceeded_value', float('inf'))
                min_exceeded = min(min_exceeded, exceeded_val)
        
        if found:
            yield {
                'current': goal,
                'frontier': [],
                'explored': explored_total.copy(),
                'came_from': {},
                'found': True,
                'path': final_path,
                'iteration': iteration,
                'frontier_size': 0,
                'path_cost': final_cost,
                'threshold': threshold,
                'ida_iteration': ida_iteration
            }
            return
        
        if min_exceeded == float('inf'):
            # No path exists
            yield {
                'current': None,
                'frontier': [],
                'explored': explored_total.copy(),
                'came_from': {},
                'found': False,
                'path': None,
                'iteration': iteration,
                'frontier_size': 0,
                'threshold': threshold,
                'ida_iteration': ida_iteration
            }
            return
        
        # Increase threshold for next iteration
        threshold = min_exceeded


def _ida_search(grid, path, g, threshold, goal, explored_total, iteration):
    """
    Recursive helper for IDA*.
    
    @param grid: Grid object
    @param path: Current path (list of cells)
    @param g: Cost to reach current node
    @param threshold: Current f-cost threshold
    @param goal: Goal cell
    @param explored_total: Set of all explored cells
    @param iteration: Current iteration count
    @yields: State dictionaries
    """
    current = path[-1]
    f = g + heuristic(current, goal)
    
    iteration += 1
    explored_total.add(current)
    
    if f > threshold:
        yield {
            'current': current,
            'explored': explored_total,
            'found': False,
            'exceeded': True,
            'exceeded_value': f,
            'iteration': iteration
        }
        return
    
    yield {
        'current': current,
        'explored': explored_total,
        'found': False,
        'iteration': iteration
    }
    
    if current == goal:
        yield {
            'current': current,
            'explored': explored_total,
            'found': True,
            'path': list(path),
            'path_cost': g,
            'iteration': iteration
        }
        return
    
    min_exceeded = float('inf')
    
    for neighbor in grid.get_neighbors(current):
        if neighbor not in path:  # Avoid cycles within current path
            path.append(neighbor)
            new_g = g + grid.get_cost(current, neighbor)
            
            for state in _ida_search(grid, path, new_g, threshold, goal,
                                      explored_total, iteration):
                iteration = state.get('iteration', iteration)
                yield state
                
                if state.get('found'):
                    return
                
                if state.get('exceeded'):
                    exceeded_val = state.get('exceeded_value', float('inf'))
                    min_exceeded = min(min_exceeded, exceeded_val)
            
            path.pop()
    
    if min_exceeded < float('inf'):
        yield {
            'current': current,
            'explored': explored_total,
            'found': False,
            'exceeded': True,
            'exceeded_value': min_exceeded,
            'iteration': iteration
        }


# =============================================================================
# ALGORITHM REGISTRY
# =============================================================================

ALGORITHMS = {
    "BFS": bfs_generator,
    "DFS": dfs_generator,
    "UCS": ucs_generator,
    "Greedy": greedy_generator,
    "A*": astar_generator,
    "IDA*": idastar_generator
}

ALGORITHM_INFO = {
    "BFS": {
        "name": "Breadth-First Search",
        "type": "Uninformed",
        "complete": True,
        "optimal": "Steps only",
        "time": "O(b^d)",
        "space": "O(b^d)"
    },
    "DFS": {
        "name": "Depth-First Search",
        "type": "Uninformed",
        "complete": False,
        "optimal": False,
        "time": "O(b^m)",
        "space": "O(bm)"
    },
    "UCS": {
        "name": "Uniform Cost Search",
        "type": "Uninformed",
        "complete": True,
        "optimal": True,
        "time": "O(b^(C*/ε))",
        "space": "O(b^(C*/ε))"
    },
    "Greedy": {
        "name": "Greedy Best-First",
        "type": "Informed",
        "complete": False,
        "optimal": False,
        "time": "O(b^m)",
        "space": "O(b^m)"
    },
    "A*": {
        "name": "A* Search",
        "type": "Informed",
        "complete": True,
        "optimal": True,
        "time": "Exponential",
        "space": "O(b^d)"
    },
    "IDA*": {
        "name": "Iterative Deepening A*",
        "type": "Informed",
        "complete": True,
        "optimal": True,
        "time": "Exponential",
        "space": "O(d)"
    }
}


def get_algorithm(name):
    """
    Get algorithm generator function by name.
    
    @param name: Algorithm name (e.g., "A*", "BFS")
    @return: Generator function or None if not found
    """
    return ALGORITHMS.get(name)


def run_algorithm_complete(grid, algorithm_name):
    """
    Run an algorithm to completion and return results.
    
    Used for benchmarking and data collection.
    
    @param grid: Grid object
    @param algorithm_name: Name of algorithm to run
    @return: AlgorithmResult object with metrics
    """
    result = AlgorithmResult(algorithm_name)
    
    algorithm = get_algorithm(algorithm_name)
    if algorithm is None:
        return result
    
    start_time = time.perf_counter()
    max_frontier = 0
    
    for state in algorithm(grid):
        result.iterations += 1
        frontier_size = state.get('frontier_size', 0)
        max_frontier = max(max_frontier, frontier_size)
        
        if state.get('found'):
            result.found = True
            result.path = state.get('path', [])
            result.path_cost = state.get('path_cost', 0)
            result.explored = state.get('explored', set())
            break
        
        result.explored = state.get('explored', set())
    
    result.time_taken = time.perf_counter() - start_time
    result.nodes_explored = len(result.explored)
    result.frontier_max = max_frontier
    
    return result
