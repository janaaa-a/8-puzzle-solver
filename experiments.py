"""
experiments.py - Runs BFS, A*(Manhattan), A*(Euclidean) on N random solvable boards and checks
that both heuristics are admissible and that Manhattan >= Euclidean.
"""
import random
from puzzle import random_state, manhattan, euclidean
from bfs import solve_bfs
from astar import solve_astar

random.seed(7)
N = 300
bfs_n = man_n = euc_n = 0
mismatch = bad_m = bad_e = dom = 0
for _ in range(N):
    s = random_state()
    b, m, e = solve_bfs(s), solve_astar(s, manhattan), solve_astar(s, euclidean)
    bfs_n += b["nodes_expanded"]; man_n += m["nodes_expanded"]; euc_n += e["nodes_expanded"]
    if not (b["cost"] == m["cost"] == e["cost"]):
        mismatch += 1
    last = len(b["path"]) - 1
    for k, st in enumerate(b["path"]):        # every state on the optimal path
        remaining = last - k
        bad_m += manhattan(st) > remaining
        bad_e += euclidean(st) > remaining + 1e-9
        dom += euclidean(st) > manhattan(st) + 1e-9
print("avg nodes  BFS / A*M / A*E:", bfs_n / N, man_n / N, euc_n / N)
print("cost mismatches:", mismatch, "| non-admissible M/E:", bad_m, bad_e, "| Euclid > Manhattan:", dom)
