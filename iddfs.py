"""
iddfs.py - Iterative Deepening DFS for the 8-puzzle.

Runs a depth-limited DFS with limit 1, 2, 3, ... until the goal is found.
The first limit that works gives a shortest path.

Assumptions:
  - Limits go from 1 to 31 (31 is the maximum solution length of the 8-puzzle).
  - A node at depth == limit is not expanded.
  - nodes_expanded is cumulative over ALL rounds (repeated work is counted).
  - search_depth = depth of the deepest node generated in any round.
  - Children are explored in the order Up, Down, Left, Right.
"""
import time
from puzzle import is_goal, is_solvable, build_result, reconstruct_path, get_neighbors


def solve_iddfs(start_state):
    """
    Solves the 8-puzzle using Iterative Deepening DFS.

    Parameters:
        start_state (tuple): 9 integers, 0 = blank.

    Returns:
        dict with: path, moves, cost, nodes_expanded, search_depth, time.
        If the puzzle is unsolvable, cost is -1 and path/moves are empty.
    """
    start_time = time.perf_counter()

    # Unsolvable boards: skip all 31 rounds of useless searching.
    if not is_solvable(start_state):
        return build_result([], [], -1, 0, start_time)

    # The start state might already be the goal.
    if is_goal(start_state):
        return build_result([start_state], [], 0, 0, start_time)

    # These counters live outside the limit loop so they accumulate over rounds.
    nodes_expanded = 0
    max_depth = 0

    for limit in range(1, 32):
        # Fresh data for every round.
        frontier = [(start_state, 0, None, None)]   # (state, depth, parent, move)
        parents = {}        # state -> (parent_state, move) for path rebuilding
        best_depth = {}     # state -> shallowest depth it was reached at this round

        while frontier:
            state, depth, parent, move = frontier.pop()

            # Skip this visit unless it reaches the state at a SHALLOWER depth.
            # A plain visited set would be wrong here: if a state is first
            # reached by a long detour, it would block the short path to it,
            # and the search could miss a solution that fits within the limit.
            if state in best_depth and best_depth[state] <= depth:
                continue

            # Record the best depth and the route (overwritten if a shorter one is found).
            best_depth[state] = depth
            if parent is None:
                parents[state] = None
            else:
                parents[state] = (parent, move)

            # Depth limit reached: do not expand (and do not count) this node.
            if depth == limit:
                continue

            nodes_expanded += 1

            # Reverse order so that Up is explored first.
            for move_name, neighbor in reversed(get_neighbors(state)):
                if neighbor in best_depth and best_depth[neighbor] <= depth + 1:
                    continue

                max_depth = max(max_depth, depth + 1)   # deepest node generated so far

                if is_goal(neighbor):
                    parents[neighbor] = (state, move_name)
                    path, moves = reconstruct_path(parents, neighbor)
                    return build_result(path, moves, nodes_expanded, max_depth, start_time)

                frontier.append((neighbor, depth + 1, state, move_name))

    # Only reached if no solution exists within 31 moves.
    return build_result([], [], nodes_expanded, max_depth, start_time)