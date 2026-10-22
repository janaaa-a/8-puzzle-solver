"""
gui_tk.py - Tkinter visualizer for the 8-puzzle solvers.

HOW TKINTER WORKS
    1. Create widgets (Label, Button, Frame) and place them in a window.
    2. Give each button a `command`: the function to call when it is clicked.
    3. root.mainloop() waits for clicks forever and calls those functions.
    The solvers (bfs.py, astar.py, ...) know nothing about the GUI. They return
    a result dict, and this file just displays result["path"] step by step.
"""

import tkinter as tk

from puzzle import GOAL, manhattan, euclidean, random_state, print_solution
from bfs import solve_bfs
from astar import solve_astar
from dfs import solve_dfs
from iddfs import solve_iddfs
STEP_DELAY = 500                 # milliseconds between steps while playing


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        root.title("8-Puzzle Solver")

        # ---- The variables the screen shows ----
        self.board = random_state()      # the puzzle to solve
        self.result = None               # result dict from the last solve
        self.step = 0                    # which state of result["path"] is shown
        self.playing = False
        self.after_id = None             # id of the scheduled "next step" call

        # ---- Board: nine labels in a 3x3 grid ----
        board_frame = tk.Frame(root)
        board_frame.grid(row=0, column=0, padx=15, pady=15)
        self.tiles = []
        for i in range(9):
            tile = tk.Label(board_frame, width=3, height=1, font=("Arial", 36, "bold"))
            tile.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            self.tiles.append(tile)

        # ---- Playback controls under the board ----
        controls = tk.Frame(root)
        controls.grid(row=1, column=0, pady=(0, 15))
        tk.Button(controls, text="< Prev", command=self.prev_step).pack(side="left", padx=3)
        self.play_button = tk.Button(controls, text="Play", width=6, command=self.toggle_play)
        self.play_button.pack(side="left", padx=3)
        tk.Button(controls, text="Next >", command=self.next_step).pack(side="left", padx=3)
        tk.Button(controls, text="Reset", command=self.reset).pack(side="left", padx=3)

        # ---- Right panel: algorithm buttons and statistics ----
        panel = tk.Frame(root)
        panel.grid(row=0, column=1, rowspan=2, padx=15, pady=15, sticky="n")

        tk.Button(panel, text="Shuffle (new random board)", command=self.shuffle).pack(fill="x", pady=(0, 10))

        algorithms = [
            ("BFS", solve_bfs),
            ("A* (Manhattan)", lambda s: solve_astar(s, manhattan)),
            ("A* (Euclidean)", lambda s: solve_astar(s, euclidean)),
            ("DFS", solve_dfs),
            ("Iterative DFS", solve_iddfs),
        ]
        for name, func in algorithms:
            # name=name, func=func freezes this loop pass's values inside the lambda
            tk.Button(
                panel, text=name, width=24,
                command=lambda name=name, func=func: self.solve(name, func),
                state="normal" if func else "disabled",
            ).pack(fill="x", pady=2)

        self.info = tk.Label(panel, text="Pick an algorithm to solve the board",
                             justify="left", anchor="w", font=("Arial", 11))
        self.info.pack(fill="x", pady=(15, 0))

        self.show()

    # ------------------------------------------------------------ showing
    def current_state(self):
        if self.result and self.result["path"]:
            return self.result["path"][self.step]
        return self.board

    def show(self):
        """Redraws the nine tiles (and the info text) from the variables."""
        state = self.current_state()
        for i, number in enumerate(state):
            if number == 0:
                self.tiles[i].config(text="", bg="#dddddd")           # blank
            elif number == GOAL[i]:
                self.tiles[i].config(text=str(number), bg="#3caa78", fg="white")  # in place
            else:
                self.tiles[i].config(text=str(number), bg="#4682c8", fg="white")

        if self.result and self.result["cost"] != -1:
            r = self.result
            move = "Start" if self.step == 0 else r["moves"][self.step - 1]
            self.info.config(text=(
                f"Algorithm: {self.algorithm}\n"
                f"Step {self.step} / {len(r['path']) - 1}   Move: {move}\n\n"
                f"Path cost: {r['cost']}\n"
                f"Nodes expanded: {r['nodes_expanded']}\n"
                f"Search depth: {r['search_depth']}\n"
                f"Running time: {r['time']} s"
            ))

    # ------------------------------------------------------------ actions
    def solve(self, name, func):
        self.stop()
        self.info.config(text=f"Solving with {name}...")
        self.root.update()               # redraw NOW; the window freezes while the solver runs
        result = func(self.board)

        self.algorithm = name
        self.result = result
        self.step = 0
        if result["cost"] == -1:
            self.info.config(text="This board is unsolvable.")
        self.show()

        # Traceable output in the terminal (very long paths would flood it)
        print(f"\n===== {name} =====")
        if result["cost"] <= 60:
            print_solution(result)
        else:
            print(f"Path has {result['cost']} steps (too long to print).")

    def shuffle(self):
        self.stop()
        self.board = random_state()
        self.result = None
        self.step = 0
        self.info.config(text="New board. Pick an algorithm.")
        self.show()

    def has_path(self):
        return self.result is not None and len(self.result["path"]) > 0

    def next_step(self):
        if self.has_path() and self.step < len(self.result["path"]) - 1:
            self.step += 1
            self.show()

    def prev_step(self):
        if self.has_path() and self.step > 0:
            self.step -= 1
            self.show()

    def reset(self):
        self.stop()
        self.step = 0
        self.show()

    def toggle_play(self):
        if not self.has_path():
            return
        if self.playing:
            self.stop()
            return
        if self.step >= len(self.result["path"]) - 1:
            self.step = 0                # finished before: start again
            self.show()
        self.playing = True
        self.play_button.config(text="Pause")
        self.tick()

    def tick(self):
        """Advance one step, then ask Tkinter to call tick() again after a delay."""
        if self.step < len(self.result["path"]) - 1:
            self.next_step()
            self.after_id = self.root.after(STEP_DELAY, self.tick)
        else:
            self.stop()

    def stop(self):
        self.playing = False
        self.play_button.config(text="Play")
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None


def run():
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()                      # wait for clicks until the window is closed


if __name__ == "__main__":
    run()