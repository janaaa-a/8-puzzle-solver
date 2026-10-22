import math
import random
"""
puzzle.py - shared helpers for the 8-puzzle solver.

Every algorithm (BFS, DFS, IDDFS, A*) and the GUI import from this file.
STATE REPRESENTATION
    A state is a tuple of 9 integers. 0 is the blank.
    Index layout:        Example (1,2,5,3,4,0,6,7,8):
        0 1 2                1 2 5
        3 4 5                3 4 _
        6 7 8                6 7 8
    Tuples are used (not lists) because they are immutable and can be used as dictionary keys.
"""


# Goal state
GOAL = (0, 1, 2, 3, 4, 5, 6, 7, 8)

# Each move describes where the BLANK moves.
# (row change, column change). The order here is the order neighbors are generated in, which matters for tie breaking in DFS. 
# generated in, which matters for tie-breaking in DFS. 
MOVES = (
    ("Up", -1, 0),
    ("Down", 1, 0),
    ("Left", 0, -1),
    ("Right", 0, 1),
)
def is_goal(state):
    #returns true if the state equals the goal state
    return state == GOAL


def get_neighbors(state):
    """
    Generates every state reachable with one legal move.

    Returns:
        list of (move_name, new_state) tuples, in the order Up, Down, Left, Right.
    """
    neighbors = []
    blank = state.index(0)             # position of the blank in the flat tuple
    row, col = divmod(blank, 3)        # convert the index to (row = blank//3, column = blank % 3) in a 3x3 board 

    for name, d_row, d_col in MOVES:
        new_row, new_col = row + d_row, col + d_col

        # Skip moves that would push the blank off the board.
        if not (0 <= new_row < 3 and 0 <= new_col < 3):
            continue

        target = new_row * 3 + new_col  # index of the tile the blank swaps with (from (row, col) back to flat index)

        # Tuples can't be changed, so copy to a list, swap, convert back.
        new_state = list(state)
        new_state[blank], new_state[target] = new_state[target], new_state[blank]
        neighbors.append((name, tuple(new_state)))

    return neighbors


def is_solvable(state):
    """
    Checks whether the goal can be reached from this state.

    An inversion is a pair of tiles (ignoring the blank) where a bigger
    number appears before a smaller one. On a 3x3 board a state is solvable
    exactly when its number of inversions is even. Half of all random
    arrangements are unsolvable.
    """
    tiles = [t for t in state if t != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions % 2 == 0


def _goal_position(tile):
    """
    (row, col) of a tile in the goal state.
    In GOAL, tile v sits at index v, so its position is divmod(v, 3).
    """
    return divmod(tile, 3)


def manhattan(state):
    """
    Manhattan heuristic: for every tile, row difference + col difference
    from its goal cell, summed over all tiles. The blank (0) is NOT counted,
    otherwise the heuristic could overestimate the true cost.
    """
    total = 0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        row, col = divmod(index, 3)
        goal_row, goal_col = _goal_position(tile)
        total += abs(row - goal_row) + abs(col - goal_col)
    return total


def euclidean(state):
    """
    Euclidean heuristic: straight-line distance sqrt(dx^2 + dy^2) from each
    tile to its goal cell, summed over all tiles (blank excluded).
    """
    total = 0.0
    for index, tile in enumerate(state):
        if tile == 0:
            continue
        row, col = divmod(index, 3)
        goal_row, goal_col = _goal_position(tile)
        total += math.sqrt((row - goal_row) ** 2 + (col - goal_col) ** 2)
    return total


def random_state():
    """Returns a random SOLVABLE state (reshuffles until it is solvable)."""
    tiles = list(range(9))
    while True:
        random.shuffle(tiles)
        state = tuple(tiles)
        if is_solvable(state):
            return state


def parse_state(text):
    """
    Converts a string like '1,2,5,3,4,0,6,7,8' 
    into a state tuple. Raises ValueError if it isn't a valid board.
    """
    state = tuple(int(x) for x in text.replace(" ", "").split(","))
    if sorted(state) != list(range(9)):
        raise ValueError("A state must contain each number 0-8 exactly once.")
    return state


def board_to_string(state):
    #Returns the board as 3 lines of text, with the blank shown as '_'
    lines = []
    for r in range(3):                      # go through each row
        row = ""
        for c in range(3):                  # go through each column in that row
            tile = state[r * 3 + c]         # convert (row, col) to the flat index
            if tile == 0:
                row += "_ "
            else:
                row += str(tile) + " "
        lines.append(row.rstrip())          # remove the extra space at the end
    return "\n".join(lines)                 # glue the 3 rows together with newlines

def print_board(state):
    #Prints the board in the terminal 
    print(board_to_string(state))


def print_solution(result):
    """
    Prints a full trace of a result dict (thereturn format):
    every step's move and board, then the statistics.
    """
    if result["cost"] == -1:
        print("No solution (puzzle is unsolvable).")
        return

    for step, state in enumerate(result["path"]):
        if step == 0:
            print("Start:")
        else:
            print(f"Step {step}: {result['moves'][step - 1]}")
        print_board(state)
        print()

    print(f"Cost of path   : {result['cost']}")
    print(f"Nodes expanded : {result['nodes_expanded']}")
    print(f"Search depth   : {result['search_depth']}")
    print(f"Running time   : {result['time']} s")


