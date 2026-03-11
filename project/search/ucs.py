from __future__ import annotations

import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "search"),):
    if _p not in sys.path: sys.path.insert(0, _p)

import time
from typing import Any, Dict, Optional

from utils import Graph, PriorityQueue, SearchLog, reconstruct_path


def ucs(
    graph:      Graph,
    start:      Any,
    goal:       Any,
    graph_name: str  = "graph",
    verbose:    bool = False,
) -> SearchLog:
    """
    Uniform-Cost Search (UCS)
    
    Args:
        graph: Dictionnaire {noeud: [(voisin, cout), ...]}
        start: Noeud de depart
        goal: Noeud but
        graph_name: Nom du graphe pour les logs
        verbose: Si True, affiche les etapes detaillees
    
    Returns:
        SearchLog contenant les resultats de la recherche
    """
    log = SearchLog(algorithm="UCS", graph_name=graph_name, start=start, goal=goal)

    # Initialisation
    open_list = PriorityQueue()           # File de priorite (cout g)
    closed: set = set()                    # Noeuds deja developpes
    g: Dict[Any, float] = {start: 0.0}     # Cout cumule depuis le depart
    came_from: Dict[Any, Optional[Any]] = {start: None}  # Parent pour reconstruction

    open_list.push(start, 0.0)
    t0 = time.perf_counter()

    if verbose:
        print("\n" + "="*60)
        print("  UNIFORM-COST SEARCH (UCS)")
        print("="*60)
        print(f"\nEtat initial : {start} (g=0)")
        
        # Afficher OPEN initial
        open_items = []
        if hasattr(open_list, '_finder'):
            for item, entry in open_list._finder.items():
                if entry[2] is not getattr(open_list, '_REMOVED', object()):
                    open_items.append((item, entry[0]))
        print(f"OPEN initial : {open_items}")
        print(f"CLOSED initial : {{}}")
        print("-"*60 + "\n")

    iteration = 0

    while not open_list.is_empty():
        iteration += 1
        current, g_cur = open_list.pop()

        # Ignorer si deja dans CLOSED (lazy deletion)
        if current in closed:
            continue

        # Mise a jour du log
        log.nodes_expanded += 1
        log.expansion_order.append(current)
        log.frontier_sizes.append(len(open_list))

        if verbose:
            print(f"► Iteration {iteration} — Extraction de {current}")
            print(f"   g({current}) = {g_cur:.2f}")
            
            # Afficher OPEN avant extraction
            open_items = []
            if hasattr(open_list, '_finder'):
                for item, entry in open_list._finder.items():
                    if entry[2] is not getattr(open_list, '_REMOVED', object()):
                        open_items.append((item, entry[0]))
            print(f"   OPEN avant extraction : {open_items}")
            print(f"   CLOSED : {sorted(closed) if closed else '{ }'}")

        # Test du but
        if current == goal:
            log.final_cost = g[current]
            log.path = reconstruct_path(came_from, current)
            log.execution_time = time.perf_counter() - t0
            
            if verbose:
                print(f"\n>>> BUT ATTEINT !")
                print(f"   Chemin trouve : {' -> '.join(str(n) for n in log.path)}")
                print(f"   Cout total : {log.final_cost:.2f}")
                print("="*60 + "\n")
            return log

        # Marquer comme developpe
        closed.add(current)
        if verbose:
            print(f"   -> {current} ajoute a CLOSED")

        # Explorer les voisins
        neighbors = graph.get(current, [])
        if verbose and neighbors:
            print(f"   Voisins de {current} : {[(n, c) for n, c in neighbors]}")
        elif verbose and not neighbors:
            print(f"   {current} n'a pas de voisins")

        for neighbor, cost in neighbors:
            # Calcul du nouveau cout
            tentative_g = g[current] + cost
            old_g = g.get(neighbor, float("inf"))

            if verbose:
                print(f"      -> Voisin {neighbor} (cout={cost})")
                print(f"         g_tentative = g({current}) + {cost} = {g[current]:.2f} + {cost} = {tentative_g:.2f}")

            # Si meilleur chemin trouve
            if tentative_g < old_g:
                if verbose:
                    if old_g == float("inf"):
                        print(f"         -> Premier chemin vers {neighbor} (ancien g = ∞)")
                    else:
                        print(f"         -> Meilleur chemin trouve (ancien g = {old_g:.2f})")

                g[neighbor] = tentative_g
                came_from[neighbor] = current
                open_list.push(neighbor, tentative_g)

                if verbose:
                    print(f"         -> {neighbor} ajoute a OPEN avec priorite g={tentative_g:.2f}")
            else:
                if verbose:
                    print(f"         -> Chemin moins bon (g existant = {old_g:.2f}) - ignore")

        if verbose:
            # Afficher OPEN apres iteration
            open_items = []
            if hasattr(open_list, '_finder'):
                for item, entry in open_list._finder.items():
                    if entry[2] is not getattr(open_list, '_REMOVED', object()):
                        open_items.append((item, entry[0]))
            print(f"   OPEN apres iteration : {open_items}")
            print("-"*60 + "\n")

    # Aucun chemin trouve
    log.execution_time = time.perf_counter() - t0
    if verbose:
        print(f"\n>>> AUCUN CHEMIN trouve vers {goal}")
        print("="*60 + "\n")
    return log