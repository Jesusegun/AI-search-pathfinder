from collections import deque
import heapq
import time

from utils import heuristic, reconstruct_path, calculate_path_cost


class AlgorithmResult:
    def __init__(self, algorithm_name):
        self.algorithm_name = algorithm_name
        self.path = []
        self.explored = set()
        self.frontier_max = 0
        self.nodes_explored = 0
        self.path_cost = 0
        self.time_taken = 0
        self.found = False
        self.iterations = 0


def bfs_generator(grid):
    start = grid.start
    goal = grid.goal
    
    frontier = deque([start])
    came_from = {start: None}
    explored = set()
    iteration = 0
    
    while frontier:
        current = frontier.popleft()
        
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
        
        for neighbor in grid.get_neighbors(current):
            if neighbor not in came_from:
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


def dfs_generator(grid):
    start = grid.start
    goal = grid.goal
    
    frontier = [start]  # LIFO stack
    came_from = {start: None}
    explored = set()
    iteration = 0
    
    while frontier:
        current = frontier.pop()
        
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
    start = grid.start
    goal = grid.goal
    
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


def greedy_generator(grid):
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
    start = grid.start
    goal = grid.goal
    
    counter = 0
    h_start = heuristic(start, goal)
    frontier = [(h_start, counter, start)]
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
    start = grid.start
    goal = grid.goal
    
    threshold = heuristic(start, goal)
    explored_total = set()
    iteration = 0
    ida_iteration = 0  # Which threshold iteration
    
    while True:
        ida_iteration += 1
        
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
        
        threshold = min_exceeded


def _ida_search(grid, path, g, threshold, goal, explored_total, iteration):
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
        if neighbor not in path:
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
