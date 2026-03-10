
from __future__ import annotations

import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "search"),):
    if _p not in sys.path: sys.path.insert(0, _p)

import time
from typing import Any, Dict, Optional

from utils import Graph, Heuristic, PriorityQueue, SearchLog, reconstruct_path


def greedy_best_first(
    graph:      Graph,
    start:      Any,
    goal:       Any,
    heuristic:  Heuristic,
    graph_name: str  = "graph",
    verbose:    bool = False,
) -> SearchLog:

    log = SearchLog(algorithm="Greedy", graph_name=graph_name, start=start, goal=goal)

    open_list = PriorityQueue()
    closed:    set                      = set()
    g:         Dict[Any, float]         = {start: 0.0}
    came_from: Dict[Any, Optional[Any]] = {start: None}

    open_list.push(start, heuristic(start, goal))
    t0 = time.perf_counter()

    while not open_list.is_empty():
        current, h_cur = open_list.pop()

        if current in closed:
            continue

        log.nodes_expanded += 1
        log.expansion_order.append(current)
        log.frontier_sizes.append(len(open_list))

        if verbose:
            print(f"  [Greedy] Extrait : {current}  h={h_cur:.2f}  "
                  f"g={g.get(current,0):.2f}  OPEN={len(open_list)}")

        if current == goal:
            log.final_cost     = g[current]
            log.path           = reconstruct_path(came_from, current)
            log.execution_time = time.perf_counter() - t0
            return log

        closed.add(current)

        for neighbor, cost in graph.get(current, []):
            if neighbor not in closed:
                tentative_g = g[current] + cost
                if tentative_g < g.get(neighbor, float("inf")):
                    g[neighbor]         = tentative_g
                    came_from[neighbor] = current
                open_list.push(neighbor, heuristic(neighbor, goal))

    log.execution_time = time.perf_counter() - t0
    return log
