"""
main.py - Runs all five algorithms (BFS, DFS, IDS, A* Manhattan, A* Euclidean)
on one 8-puzzle board from the terminal.

Usage:
    python main.py                      # random solvable board
    python main.py "1,2,5,3,4,0,6,7,8"  # a given board (0 = blank)
"""
import sys
import os
import re
from contextlib import redirect_stdout

from puzzle import random_state, parse_state, manhattan, euclidean, is_solvable, print_solution
from bfs import solve_bfs
from dfs import solve_dfs
from iddfs import solve_iddfs
from astar import solve_astar


def get_start_state():
    """Returns the board from the command line, or a random solvable one."""
    if len(sys.argv) > 1:
        try:
            return parse_state(sys.argv[1])
        except ValueError:
            print("Invalid board. Use nine numbers 0-8, each once, "
                  "e.g. \"1,2,5,3,4,0,6,7,8\"")
            sys.exit(1)
    return random_state()


# (name, function) pairs. Each function takes a start state and returns the
# shared result dict. A* needs a heuristic, so a lambda fixes it for each run.
ALGORITHMS = [
    ("BFS", solve_bfs),
    ("DFS", solve_dfs),
    ("Iterative DFS", solve_iddfs),
    ("A* (Manhattan)", lambda s: solve_astar(s, manhattan)),
    ("A* (Euclidean)", lambda s: solve_astar(s, euclidean)),
]

def run_all(start):
    """Runs every algorithm on the same board; returns {name: result dict}."""
    results = {}
    for name, solver in ALGORITHMS:
        print(f"Running {name}...")
        results[name] = solver(start)
    return results


def print_table(results):
    """Prints one row per algorithm with the measurements the report needs."""
    header = f"{'Algorithm':<16}{'Cost':>8}{'Expanded':>12}{'Depth':>10}{'Time (s)':>12}"
    print(header)
    print("-" * len(header))
    for name, r in results.items():
        print(f"{name:<16}{r['cost']:>8}{r['nodes_expanded']:>12}"
              f"{r['search_depth']:>10}{r['time']:>12}")

def save_traces(start, results, folder="traces"):
    """Writes the full step-by-step trace of every algorithm to its own text file."""
    os.makedirs(folder, exist_ok=True)
    for name, r in results.items():
        # "A* (Manhattan)" contains characters Windows doesn't allow in file
        # names, so keep only letters and digits, and join the pieces with "_".
        filename = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") + ".txt"
        path = os.path.join(folder, filename)
        with open(path, "w", encoding="utf-8") as f:
            # print_solution prints to the screen; redirect_stdout sends the
            # same output into the file instead.
            with redirect_stdout(f):
                print(f"Algorithm: {name}")
                print(f"Start state: {start}")
                print()
                print_solution(r)
        print(f"  saved {path}")

if __name__ == "__main__":
    start = get_start_state()
    print("Start state:", start)

    if not is_solvable(start):
        print("This board is unsolvable (odd number of inversions).")
        sys.exit(0)

    results = run_all(start)
    print()
    print_table(results)

    print("\nSaving full traces...")
    save_traces(start, results)

    sample = results["A* (Manhattan)"]
    if sample["cost"] <= 60:
        print("\nSample trace: A* (Manhattan)\n")
        print_solution(sample)