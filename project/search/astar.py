
from __future__ import annotations

import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "search"),):
    if _p not in sys.path: sys.path.insert(0, _p)

import time
from typing import Any, Dict, List, Optional

from utils import Graph, Heuristic, PriorityQueue, SearchLog, reconstruct_path


def astar(
    graph:      Graph,
    start:      Any,
    goal:       Any,
    heuristic:  Heuristic,
    weight:     float = 1.0,
    graph_name: str   = "graph",
    verbose:    bool  = False,
) -> SearchLog:

    algo_name = "A*" if weight == 1.0 else f"WA*(w={weight})"
    log = SearchLog(algorithm=algo_name, graph_name=graph_name, start=start, goal=goal)

    open_list = PriorityQueue()
    closed:    set                      = set()
    g:         Dict[Any, float]         = {start: 0.0}
    came_from: Dict[Any, Optional[Any]] = {start: None}

    open_list.push(start, g[start] + weight * heuristic(start, goal))
    t0 = time.perf_counter()

    while not open_list.is_empty():
        current, f_cur = open_list.pop()

        log.nodes_expanded += 1
        log.expansion_order.append(current)
        log.frontier_sizes.append(len(open_list))

        if verbose:
            print(f"  [A*(w={weight})] Extrait : {current}  "
                  f"g={g[current]:.2f}  f={f_cur:.2f}  OPEN={len(open_list)}")

        if current == goal:
            log.final_cost     = g[current]
            log.path           = reconstruct_path(came_from, current)
            log.execution_time = time.perf_counter() - t0
            return log

        closed.add(current)

        for neighbor, edge_cost in graph.get(current, []):
            tentative_g = g[current] + edge_cost

            # Ignorer si CLOSED et pas d'amelioration (h coherente)
            if neighbor in closed and tentative_g >= g.get(neighbor, float("inf")):
                continue

            if tentative_g < g.get(neighbor, float("inf")):
                g[neighbor]         = tentative_g
                came_from[neighbor] = current
                open_list.push(neighbor, tentative_g + weight * heuristic(neighbor, goal))
                # Reouverture si meilleur chemin (h non coherente)
                if neighbor in closed:
                    closed.discard(neighbor)

    log.execution_time = time.perf_counter() - t0
    return log
