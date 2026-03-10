
from __future__ import annotations
import sys, os, json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "search"),):
    if _p not in sys.path: sys.path.insert(0, _p)
if _ROOT not in sys.path: sys.path.insert(0, _ROOT)

from typing import Any, Dict, List, Tuple
from utils import Graph, Heuristic, generate_random_graph, make_dict_heuristic

_DATA_DIR = os.path.join(_ROOT, "data")


# ============================================================
#  Chargement depuis graph_cours.json
# ============================================================

def _load_graph_cours() -> dict:
    with open(os.path.join(_DATA_DIR, "graph_cours.json"), encoding="utf-8") as f:
        return json.load(f)

def _load_benchmark_config() -> dict:
    with open(os.path.join(_DATA_DIR, "benchmark_config.json"), encoding="utf-8") as f:
        return json.load(f)


_gc = _load_graph_cours()

# Graphe : S -> A -> C -> G  (exact cours)
GRAPH_COURS: Graph = {
    node: [(v, float(c)) for v, c in neighbors]
    for node, neighbors in _gc["graph"].items()
}

SOURCE_COURS: str = _gc["start"]   # "S"
GOAL_COURS:   str = _gc["goal"]    # "G"

# Heuristiques depuis graph_cours.json
H_ADMISSIBLE_COHERENTE:     Dict[str, float] = _gc["heuristics"]["admissible_coherente"]
H_ADMISSIBLE_NON_COHERENTE: Dict[str, float] = _gc["heuristics"]["admissible_non_coherente"]
H_NON_ADMISSIBLE:           Dict[str, float] = _gc["heuristics"]["non_admissible"]

OPTIMAL_SOLUTION = _gc.get("optimal_solution", {})


# ============================================================
#  Graphes de benchmark
# ============================================================

def get_benchmark_graphs() -> List[Tuple[Graph, str, Any, Any]]:
    """
    Retourne [(graph, name, start, goal)].
    Graphe du cours + graphes aleatoires depuis benchmark_config.json.
    """
    cfg    = _load_benchmark_config()
    graphs = [(GRAPH_COURS, "cours", SOURCE_COURS, GOAL_COURS)]
    for entry in cfg["graphs"]:
        g, name = generate_random_graph(
            n_nodes = entry["n_nodes"],
            n_edges = entry["n_edges"],
            seed    = entry["seed"],
            name    = entry["name"],
        )
        graphs.append((g, name, 0, entry["n_nodes"] - 1))
    return graphs


def get_weighted_astar_weights() -> List[float]:
    return _load_benchmark_config()["weighted_astar_weights"]
