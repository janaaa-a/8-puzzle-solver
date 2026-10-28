"""
- Tkinter visualizer for the 8-puzzle solvers.

HOW TKINTER WORKS
    1. Create widgets (Label, Button, Frame) and place them in a window.
    2. Give each button a `command`: the function to call when it is clicked.
    3. root.mainloop() waits for clicks forever and calls those functions.
"""

import tkinter as tk

from puzzle import GOAL, manhattan, euclidean, random_state, print_solution, is_solvable
from bfs import solve_bfs
from astar import solve_astar
from dfs import solve_dfs
from iddfs import solve_iddfs
STEP_DELAY = 500                 # milliseconds between steps while playing


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        root.title("8-Puzzle Solver")
        root.geometry("760x480")                 # starting size of the window
        root.minsize(640, 420)                   # don't let it shrink too far
        root.columnconfigure(0, weight=1)        # the board column takes all extra width
        root.rowconfigure(0, weight=1)           # the board row takes all extra height
        self.tile_font = ("Arial", 36, "bold")   # replaced by a bigger/smaller font on resize

        #  The variables the screen shows
        self.board = random_state()      # the puzzle to solve
        self.result = None               # result dict from the last solve
        self.step = 0                    # which state of result["path"] is shown
        self.playing = False
        self.after_id = None             # id of the scheduled "next step" call
        self.drag_from = None            # index (0-8) of the tile being dragged, or None
        self.ghost = None                # the floating copy of the tile while dragging

        # ---- Board: nine labels in a 3x3 grid ----
        board_frame = tk.Frame(root)                          # 1. create the frame FIRST
        board_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        for k in range(3):                                    # 2. rows and columns that stretch
            board_frame.rowconfigure(k, weight=1, uniform="cell")
            board_frame.columnconfigure(k, weight=1, uniform="cell")
        board_frame.bind("<Configure>", self.resize_tiles)    # 3. call resize_tiles when it changes size

        self.tiles = []
        for i in range(9):
            tile = tk.Label(board_frame, width=1, height=1, font=self.tile_font)
            tile.grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky="nsew")
            tile.bind("<ButtonPress-1>", lambda e, i=i: self.on_press(i, e))
            tile.bind("<B1-Motion>", self.on_drag)
            tile.bind("<ButtonRelease-1>", self.on_release)
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

    def resize_tiles(self, event):
        """Board area changed size: make the numbers big enough for the new tile size."""
        cell = min(event.width, event.height) // 3          # size of one tile in pixels
        size = max(12, int(cell * 0.45))
        self.tile_font = ("Arial", -size, "bold")           # negative = size in pixels
        for tile in self.tiles:
            tile.config(font=self.tile_font)

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
        if result["cost"] != -1 and result["cost"] <= 200:   # unsolvable or very long (DFS) paths: don't autoplay
            self.toggle_play()
        self.show()

        # Traceable output in the terminal (very long paths would flood it)
        print(f"\n===== {name} =====")
        if result["cost"] <= 60:
            print_solution(result)
        else:
            print(f"Path has {result['cost']} steps (too long to print).")
    
    def on_release(self, event):
        """Mouse released: drop the tile onto whatever tile is under the mouse."""
        if self.drag_from is None:
            return
        source = self.drag_from
        self.drag_from = None

        # Remove the floating tile FIRST, otherwise it is the widget under the mouse.
        if self.ghost is not None:
            self.ghost.destroy()
            self.ghost = None

        # Which widget is under the mouse right now?
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget in self.tiles:
            target = self.tiles.index(widget)
            if target != source:
                board = list(self.board)                       # tuples can't be changed
                board[source], board[target] = board[target], board[source]
                self.board = tuple(board)
                if is_solvable(self.board):
                    self.info.config(text="Board changed. Pick an algorithm.")
                else:
                    self.info.config(text="Board changed, but it is UNSOLVABLE.\nSwap two tiles again to fix it.")

        self.show()    # redraw: shows the swap, or restores the grey tile if dropped outside

    def on_press(self, i, event):
        """Mouse pressed on tile i: start a drag."""
        self.stop()                              # stop Play if it was running
        if self.result:                          # drop any shown solution, edit the real board
            self.result = None
            self.step = 0
            self.info.config(text="Drag a tile onto another tile to swap them.")
            self.show()
        self.drag_from = i
        number = self.board[i]
        self.tiles[i].config(bg="#999999")       # grey out the tile we picked up
        self.ghost = tk.Label(self.root, text=str(number) if number else "",
                            font=self.tile_font, width=3, height=1,
                            bg="#f0a030" if number else "#dddddd", fg="white")
        self.move_ghost(event)

    def move_ghost(self, event):
        """Puts the floating tile centred under the mouse."""
        x = event.x_root - self.root.winfo_rootx()   # screen coords -> window coords
        y = event.y_root - self.root.winfo_rooty()
        self.ghost.place(x=x, y=y, anchor="center",
                 width=self.tiles[0].winfo_width(), height=self.tiles[0].winfo_height())

    def on_drag(self, event):
        """Mouse moved while the button is held: the floating tile follows it."""
        if self.ghost is not None:
            self.move_ghost(event)

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