import time 
from puzzle import is_goal, is_solvable, build_result, reconstruct_path, get_neighbors

def solve_iddfs(start_state):

    start_time = time.perf_counter()
    if not is_solvable(start_state) :
        return build_result([], [], 0, 0, start_time)
    if is_goal(start_state):
        return build_result([start_state], [], 0, 0, start_time)

    nodes_expanded = 0
    max_depth = 0

    for limit in range(1, 32):

        stack = [(start_state, 0, None, None)]
        parents = {}
        best_depth = {}

        while stack:
            state, depth, parent, move = stack.pop()

            if state in best_depth and best_depth[state] <= depth:
                continue

            best_depth[state] = depth
            if parent is None:
                parents[state] = None
            else:
                parents[state] = (parent, move)

            if depth == limit:
                continue

            nodes_expanded += 1

            for move_name, neighbor in reversed(get_neighbors(state)):

                if neighbor in best_depth and best_depth[neighbor] <= depth + 1:
                    continue

                max_depth = depth + 1

                if is_goal(neighbor):
                    parents[neighbor] = (state, move_name)
                    path, moves = reconstruct_path(parents, neighbor)
                    return build_result(path, moves, nodes_expanded, max_depth, start_time)

                stack.append((neighbor, depth + 1, state, move_name))

    return build_result([], [], nodes_expanded, max_depth, start_time)