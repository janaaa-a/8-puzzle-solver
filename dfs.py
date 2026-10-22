import time 
from puzzle import is_goal, is_solvable, build_result, reconstruct_path, get_neighbors

def solve_dfs(start_state):

    start_time = time.perf_counter()
    if not is_solvable(start_state) :
        return build_result([], [], 0, 0, start_time)
    if is_goal(start_state):
        return build_result([start_state], [], 0, 0, start_time)

    stack = [(start_state, 0, None, None)]
    parents = {}
    nodes_expanded = 0
    max_depth = 0

    while stack:
        state, depth, parent, move = stack.pop()
        if state in parents:
            continue
        if parent is None:
            parents[state] = None
        else:
            parents[state] = (parent, move)

        nodes_expanded += 1

        for move_name, neighbor in reversed(get_neighbors(state)):
            if neighbor in parents:
                continue

            max_depth = depth + 1

            if is_goal(neighbor):
                parents[neighbor] = (state, move_name)
                path, moves = reconstruct_path(parents, neighbor)

                return build_result(path, moves, nodes_expanded, max_depth, start_time)
            else:
                stack.append((neighbor, depth + 1, state, move_name))

    return build_result([], [], nodes_expanded, max_depth, start_time)