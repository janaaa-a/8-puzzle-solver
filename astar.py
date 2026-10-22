#astar.py - A* search for the 8-puzzle.
import heapq
import time
from puzzle import is_goal, get_neighbors, is_solvable, manhattan, euclidean , reconstruct_path, build_result
 
 
def solve_astar(start_state, heuristic=manhattan):
    """
    Solves the 8-puzzle using A* search.
 
    Parameters:
        start_state (tuple): 9 integers, 0 = blank.
        heuristic (function): manhattan or euclidean (both from puzzle.py).
 
    Returns:
        dict with: path, moves, cost, nodes_expanded, search_depth, time.
        If the puzzle is unsolvable, cost is -1 and path/moves are empty.
    """
    start_time = time.perf_counter()
 
    # Unsolvable boards: return immediately instead of searching everything.
    if not is_solvable(start_state):
        return build_result([], [], 0, 0, start_time)
 
    # The start state might already be the goal.
    if is_goal(start_state):
        return build_result([start_state], [], 0, 0, start_time)
 
    # Frontier = priority queue (min-heap) of (f, h, counter, state).
    #  - f decides which state is expanded next.
    #  - h breaks ties in favour of states that look closer to the goal.
    #  - counter breaks any remaining ties (first generated, first expanded),
    #    so Python never has to compare two states.
    counter = 0
    start_h = heuristic(start_state)
    frontier = [(start_h, start_h, counter, start_state)]
 
    best_g = {start_state: 0}          # cheapest known cost to reach each state
    parents = {start_state: None}      # state -> (parent_state, move) for the path
    closed = set()                     # states that were already expanded
 
    nodes_expanded = 0
    max_search_depth = 0
 
    while frontier:
        _, _, _, state = heapq.heappop(frontier)
 
        # A state can be pushed more than once (when a cheaper route to it is
        # found). Skip the stale copies of states we already expanded.
        if state in closed:
            continue
 
        # Goal test when the state is POPPED (not when generated).
        # This is what guarantees A* returns an optimal path.
        if is_goal(state):
            path, moves = reconstruct_path(parents, state)
            return build_result(path, moves, nodes_expanded,
                                 max_search_depth, start_time)
 
        closed.add(state)
        nodes_expanded += 1            # expanded = we generate its children now
        g = best_g[state]
 
        for move, neighbor in get_neighbors(state):
            if neighbor in closed:     # consistent heuristic: never needs reopening
                continue
 
            new_g = g + 1              # every move costs 1
            # Only keep this route if it's the first one found, or a cheaper one.
            if neighbor not in best_g or new_g < best_g[neighbor]:
                best_g[neighbor] = new_g
                parents[neighbor] = (state, move)
                max_search_depth = max(max_search_depth, new_g)
 
                counter += 1
                h = heuristic(neighbor)
                heapq.heappush(frontier, (new_g + h, h, counter, neighbor))
 