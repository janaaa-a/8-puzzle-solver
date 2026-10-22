from collections import deque
import time
from puzzle import get_neighbors, is_goal, is_solvable, reconstruct_path, build_result

def solve_bfs(start_state):
    """
    Solves the 8-puzzle using Breadth-First Search.

    Parameters:
        start_state (tuple): 9 integers, 0 = blank.

    Returns:
        dict with: path, moves, cost, nodes_expanded, search_depth, time.
        If the puzzle is unsolvable, cost is -1 and path/moves are empty.
    """
    start_time = time.perf_counter()

    # Unsolvable boards: return immediately instead of searching everything.
    if not is_solvable(start_state):
        return _build_result([], [], 0, 0, start_time)

    # The start state might already be the goal.
    if is_goal(start_state):
        return _build_result([start_state], [], 0, 0, start_time)

    # Queue holds a tuple:(state, depth).
    queue = deque([(start_state, 0)])

    # Maps each discovered state -> (parent_state, move that led to it).
    # The start has no parent. This dict also acts as the "visited" set,
    # because a state is in it exactly when it has been discovered.
    parents = {start_state: None}

    nodes_expanded = 0
    max_search_depth = 0

    while queue:
        current_state, depth = queue.popleft()
        nodes_expanded += 1  # a node counts as expanded when we generate its children

        for move, neighbor in get_neighbors(current_state):
            if neighbor in parents:          # already discovered, skip
                continue

            parents[neighbor] = (current_state, move)
            max_search_depth = max(max_search_depth, depth + 1)

            # Goal test at generation time (the assumption to state in the report).
            if is_goal(neighbor):
                path, moves = reconstruct_path(parents, neighbor)
                return build_result(path, moves, nodes_expanded,
                                     max_search_depth, start_time)

            queue.append((neighbor, depth + 1))