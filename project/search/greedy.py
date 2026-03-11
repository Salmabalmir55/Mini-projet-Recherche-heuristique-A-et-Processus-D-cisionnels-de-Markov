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

    # Initialisation
    open_list.push(start, heuristic(start, goal))
    t0 = time.perf_counter()
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"  GREEDY BEST-FIRST SEARCH - Départ: {start} → But: {goal}")
        print(f"{'='*60}")
        print(f"\nÉtat initial : {start} (g=0, h={heuristic(start, goal):.1f})")
        
        # Afficher OPEN initial sans utiliser _finder directement
        open_items = []
        if hasattr(open_list, '_finder'):
            for item, entry in open_list._finder.items():
                if entry[2] is not getattr(open_list, '_REMOVED', object()):
                    open_items.append((item, entry[0]))
        print(f"OPEN initial : {open_items}")
        print(f"CLOSED initial : {{}}")
        print(f"{'-'*60}\n")

    iteration = 0

    while not open_list.is_empty():
        iteration += 1
        current, h_cur = open_list.pop()

        if current in closed:
            continue

        # Sauvegarde pour le log
        log.nodes_expanded += 1
        log.expansion_order.append(current)
        log.frontier_sizes.append(len(open_list))

        if verbose:
            # Affichage détaillé de l'itération
            print(f"► Itération {iteration} — Extraction de {current}")
            print(f"   h({current}) = {h_cur:.1f}")
            print(f"   g({current}) = {g[current]:.1f}")
            
            # Afficher OPEN actuel
            open_items = []
            if hasattr(open_list, '_finder'):
                for item, entry in open_list._finder.items():
                    if entry[2] is not getattr(open_list, '_REMOVED', object()):
                        open_items.append((item, round(entry[0], 1)))
            print(f"   OPEN avant extraction : {open_items}")
            print(f"   CLOSED : {sorted(closed) if closed else '{}'}")

        if current == goal:
            log.final_cost = g[current]
            log.path = reconstruct_path(came_from, current)
            log.execution_time = time.perf_counter() - t0
            if verbose:
                print(f"\n BUT ATTEINT !")
                print(f"   Chemin trouvé : {' → '.join(str(n) for n in log.path)}")
                print(f"   Coût total : {log.final_cost:.1f}")
                print(f"{'='*60}\n")
            return log

        closed.add(current)
        if verbose:
            print(f"   → {current} ajouté à CLOSED")

        # Exploration des voisins
        neighbors = graph.get(current, [])
        if verbose and neighbors:
            print(f"   Voisins de {current} : {[(n, cost) for n, cost in neighbors]}")
        elif verbose and not neighbors:
            print(f"   {current} n'a pas de voisins")

        for neighbor, cost in neighbors:
            if neighbor not in closed:
                tentative_g = g[current] + cost
                old_g = g.get(neighbor, float("inf"))
                
                if verbose:
                    print(f"      → Voisin {neighbor} (coût={cost})")
                    print(f"         g_tentative = g({current}) + {cost} = {g[current]:.1f} + {cost} = {tentative_g:.1f}")
                
                if tentative_g < old_g:
                    if verbose:
                        print(f"Meilleur chemin trouvé (ancien g={old_g if old_g != float('inf') else '∞'})")
                    
                    g[neighbor] = tentative_g
                    came_from[neighbor] = current
                    priority = heuristic(neighbor, goal)
                    open_list.push(neighbor, priority)
                    
                    if verbose:
                        print(f"         → {neighbor} ajouté à OPEN avec priorité h={priority:.1f}")
                else:
                    if verbose:
                        print(f"Chemin moins bon (g existant={old_g:.1f}) - ignoré")
            else:
                if verbose:
                    print(f"      → Voisin {neighbor} déjà dans CLOSED - ignoré")

        if verbose:
            # Afficher OPEN après itération
            open_items = []
            if hasattr(open_list, '_finder'):
                for item, entry in open_list._finder.items():
                    if entry[2] is not getattr(open_list, '_REMOVED', object()):
                        open_items.append((item, round(entry[0], 1)))
            print(f"   OPEN après itération : {open_items}")
            print(f"{'-'*60}\n")

    log.execution_time = time.perf_counter() - t0
    if verbose:
        print(f" Aucun chemin trouvé vers {goal}")
    return log
