

from __future__ import annotations
import sys
if hasattr(sys.stdout,"reconfigure") and sys.stdout.encoding and sys.stdout.encoding.lower()!="utf-8":
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

import heapq
import json
import os
import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

Graph     = Dict[Any, List[Tuple[Any, float]]]
Heuristic = Callable[[Any, Any], float]


# -- File de priorite ---------------------------------------------------------

class PriorityQueue:
    """Min-heap avec lazy deletion - permet la mise a jour de priorite en O(log n)."""

    _REMOVED = object()

    def __init__(self) -> None:
        self._heap:    List[list]      = []
        self._finder:  Dict[Any, list] = {}
        self._counter: int             = 0

    def push(self, item: Any, priority: float) -> None:
        if item in self._finder:
            self._finder[item][2] = self._REMOVED
        entry = [priority, self._counter, item]
        self._counter += 1
        self._finder[item] = entry
        heapq.heappush(self._heap, entry)

    def pop(self) -> Tuple[Any, float]:
        while self._heap:
            priority, _, item = heapq.heappop(self._heap)
            if item is not self._REMOVED:
                del self._finder[item]
                return item, priority
        raise IndexError("pop depuis une file vide")

    def get_priority(self, item: Any) -> Optional[float]:
        entry = self._finder.get(item)
        return entry[0] if entry is not None else None

    def __contains__(self, item: Any) -> bool:
        return item in self._finder

    def __len__(self) -> int:
        return len(self._finder)

    def is_empty(self) -> bool:
        return not self._finder


# -- Journalisation ------------------------------------------------------------

@dataclass
class SearchLog:
    algorithm:       str
    graph_name:      str
    start:           Any
    goal:            Any
    expansion_order: List[Any] = field(default_factory=list)
    frontier_sizes:  List[int] = field(default_factory=list)
    final_cost:      float     = float("inf")
    path:            List[Any] = field(default_factory=list)
    nodes_expanded:  int       = 0
    execution_time:  float     = 0.0

    def summary(self) -> str:
        path_str = " -> ".join(str(n) for n in self.path) if self.path else "0"
        cost_str = f"{self.final_cost:.4f}" if self.final_cost != float("inf") else "inf"
        return (
            f"+{'='*52}\n"
            f"|  Algorithme    : {self.algorithm}\n"
            f"|  Graphe        : {self.graph_name}\n"
            f"|  Source -> But  : {self.start} -> {self.goal}\n"
            f"|  Chemin        : {path_str}\n"
            f"|  Cout final    : {cost_str}\n"
            f"|  Noeuds dev.    : {self.nodes_expanded}\n"
            f"|  Temps (ms)    : {self.execution_time * 1000:.3f}\n"
            f"+{'='*52}"
        )

    def to_dict(self) -> dict:
        return {
            "algorithm":         self.algorithm,
            "graph_name":        self.graph_name,
            "start":             str(self.start),
            "goal":              str(self.goal),
            "path":              [str(n) for n in self.path],
            "final_cost":        self.final_cost,
            "nodes_expanded":    self.nodes_expanded,
            "execution_time_ms": round(self.execution_time * 1000, 4),
            "expansion_order":   [str(n) for n in self.expansion_order],
        }


def save_log(log: SearchLog, directory: str = "logs") -> None:
    os.makedirs(directory, exist_ok=True)
    fname = os.path.join(directory,
                         f"{log.algorithm}_{log.graph_name}_{log.start}_{log.goal}.json")
    with open(fname, "w", encoding="utf-8") as fh:
        json.dump(log.to_dict(), fh, indent=2, ensure_ascii=False)


# -- Reconstruction de chemin --------------------------------------------------

def reconstruct_path(came_from: Dict[Any, Optional[Any]], node: Any) -> List[Any]:
    path: List[Any] = []
    cur: Optional[Any] = node
    while cur is not None:
        path.append(cur)
        cur = came_from.get(cur)
    path.reverse()
    return path


# -- Generateur de graphes aleatoires (Extension E2) --------------------------

def generate_random_graph(
    n_nodes:  int,
    n_edges:  int,
    min_cost: float = 1.0,
    max_cost: float = 10.0,
    seed:     int   = 42,
    name:     str   = "random",
) -> Tuple[Graph, str]:
    """Graphe oriente pondere aleatoire avec connexite garantie."""
    rng   = random.Random(seed)
    nodes = list(range(n_nodes))
    graph: Graph = {n: [] for n in nodes}

    shuffled = nodes[:]
    rng.shuffle(shuffled)
    for i in range(len(shuffled) - 1):
        u, v = shuffled[i], shuffled[i + 1]
        graph[u].append((v, round(rng.uniform(min_cost, max_cost), 1)))

    existing = {(u, v) for u, nbrs in graph.items() for v, _ in nbrs}
    extra, attempts = 0, 0
    needed = max(0, n_edges - (n_nodes - 1))
    while extra < needed and attempts < 20_000:
        u = rng.randint(0, n_nodes - 1)
        v = rng.randint(0, n_nodes - 1)
        if u != v and (u, v) not in existing:
            graph[u].append((v, round(rng.uniform(min_cost, max_cost), 1)))
            existing.add((u, v))
            extra += 1
        attempts += 1

    return graph, name


# -- Heuristiques utilitaires --------------------------------------------------

def zero_heuristic(_node: Any, _goal: Any) -> float:
    return 0.0


def make_dict_heuristic(h_dict: Dict[Any, float]) -> Heuristic:
    def h(node: Any, _goal: Any) -> float:
        return h_dict.get(node, 0.0)
    return h


# -- Affichage tabulaire -------------------------------------------------------

def print_table(rows: List[Dict], title: str = "") -> None:
    if not rows:
        return
    if title:
        print(f"\n{'='*64}\n  {title}\n{'='*64}")
    keys   = list(rows[0].keys())
    widths = {k: max(len(str(k)), max(len(str(r[k])) for r in rows)) for k in keys}
    print("  " + "  ".join(str(k).ljust(widths[k]) for k in keys))
    print("  " + "  ".join("-" * widths[k] for k in keys))
    for row in rows:
        print("  " + "  ".join(str(row[k]).ljust(widths[k]) for k in keys))
    print()
