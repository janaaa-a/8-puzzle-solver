"""
dfs.py - Depth-First Search for the 8-puzzle.

The frontier is a stack (LIFO). The `parents` dictionary is both the visited
set and the record of how each state was reached.

Assumptions:
  - Children are explored in the order Up, Down, Left, Right.
  - A state is marked visited when it is POPPED (expanded), not when pushed.
  - The goal test is done when a child is generated (same as BFS).
  - search_depth = depth of the deepest node generated.
  - DFS finds a path, not necessarily the shortest one.
"""
import time
from puzzle import is_goal, is_solvable, build_result, reconstruct_path, get_neighbors


def solve_dfs(start_state):
    """
    Solves the 8-puzzle using Depth-First Search.

    Parameters:
        start_state (tuple): 9 integers, 0 = blank.

    Returns:
        dict with: path, moves, cost, nodes_expanded, search_depth, time.
        If the puzzle is unsolvable, cost is -1 and path/moves are empty.
    """
    start_time = time.perf_counter()

    # Unsolvable boards: return immediately, otherwise DFS would search
    # every reachable state before giving up.
    if not is_solvable(start_state):
        return build_result([], [], -1, 0, start_time)

    # The start state might already be the goal.
    if is_goal(start_state):
        return build_result([start_state], [], 0, 0, start_time)

    # Stack items: (state, depth, parent state, move that led here).
    frontier = [(start_state, 0, None, None)]
    parents = {}              # state -> (parent_state, move); keys = visited states
    nodes_expanded = 0
    max_depth = 0

    while frontier:
        state, depth, parent, move = frontier.pop()

        # The same state can be pushed several times before it is popped.
        # Only the first copy popped is visited; later copies are discarded.
        if state in parents:
            continue

        # Record how we reached this state (the start has no parent).
        if parent is None:
            parents[state] = None
        else:
            parents[state] = (parent, move)

        nodes_expanded += 1   # counted when popped, same meaning as in BFS

        # Push children in REVERSE order so that Up is popped (explored) first.
        for move_name, neighbor in reversed(get_neighbors(state)):
            if neighbor in parents:
                continue

            max_depth = max(max_depth, depth + 1)   # deepest node generated so far

            if is_goal(neighbor):
                parents[neighbor] = (state, move_name)
                path, moves = reconstruct_path(parents, neighbor)
                return build_result(path, moves, nodes_expanded, max_depth, start_time)

            frontier.append((neighbor, depth + 1, state, move_name))

    # Only reached if no solution exists (should not happen for solvable boards).
    return build_result([], [], nodes_expanded, max_depth, start_time)