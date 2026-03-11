from __future__ import annotations

import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "search"),):
    if _p not in sys.path: sys.path.insert(0, _p)

import time
from typing import Any, Dict, Optional

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
    """
    A* Search (et Weighted A*)
    
    Args:
        graph: Dictionnaire {noeud: [(voisin, cout), ...]}
        start: Noeud de depart
        goal: Noeud but
        heuristic: Fonction heuristique h(n, goal)
        weight: Poids pour Weighted A* (f = g + w * h)
        graph_name: Nom du graphe pour les logs
        verbose: Si True, affiche les etapes detaillees
    
    Returns:
        SearchLog contenant les resultats de la recherche
    """
    algo_name = "A*" if weight == 1.0 else f"WA*(w={weight})"
    log = SearchLog(algorithm=algo_name, graph_name=graph_name, start=start, goal=goal)

    # Initialisation
    open_list = PriorityQueue()
    closed: set = set()
    g: Dict[Any, float] = {start: 0.0}
    came_from: Dict[Any, Optional[Any]] = {start: None}

    # Initialiser OPEN avec le noeud de depart
    f_start = g[start] + weight * heuristic(start, goal)
    open_list.push(start, f_start)
    t0 = time.perf_counter()

    if verbose:
        print("\n" + "="*60)
        print(f"  {algo_name} - Recherche heuristique")
        print("="*60)
        print(f"\nEtat initial : {start}")
        print(f"   g({start}) = 0.0")
        print(f"   h({start}) = {heuristic(start, goal):.2f}")
        print(f"   f({start}) = g + {weight}*h = 0.0 + {weight}*{heuristic(start, goal):.2f} = {f_start:.2f}")
        
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
        current, f_cur = open_list.pop()

        # Ignorer si deja dans CLOSED (lazy deletion)
        if current in closed:
            continue

        # Mise a jour du log
        log.nodes_expanded += 1
        log.expansion_order.append(current)
        log.frontier_sizes.append(len(open_list))

        if verbose:
            print(f"► Iteration {iteration} — Extraction de {current}")
            print(f"   g({current}) = {g[current]:.2f}")
            print(f"   h({current}) = {heuristic(current, goal):.2f}")
            print(f"   f({current}) = {g[current]:.2f} + {weight}*{heuristic(current, goal):.2f} = {f_cur:.2f}")
            
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

        for neighbor, edge_cost in neighbors:
            # Ignorer si dans CLOSED et pas d'amelioration possible
            if neighbor in closed:
                # Verification si on peut avoir un meilleur chemin
                # (pour heuristiques non coherentes, on pourrait devoir rouvrir)
                tentative_g = g[current] + edge_cost
                if tentative_g >= g.get(neighbor, float("inf")):
                    if verbose:
                        print(f"      -> Voisin {neighbor} deja dans CLOSED avec g={g[neighbor]:.2f} - ignore")
                    continue
                # Sinon, on va le rouvrir (traitement apres)
                if verbose:
                    print(f"      -> Voisin {neighbor} dans CLOSED mais meilleur chemin trouve - reouverture")

            # Calcul du nouveau cout
            tentative_g = g[current] + edge_cost
            old_g = g.get(neighbor, float("inf"))

            if verbose:
                print(f"      -> Voisin {neighbor} (cout={edge_cost})")
                print(f"         g_tentative = g({current}) + {edge_cost} = {g[current]:.2f} + {edge_cost} = {tentative_g:.2f}")

            # Si meilleur chemin trouve
            if tentative_g < old_g:
                if verbose:
                    if old_g == float("inf"):
                        print(f"         -> Premier chemin vers {neighbor} (ancien g = ∞)")
                    else:
                        print(f"         -> Meilleur chemin trouve (ancien g = {old_g:.2f})")

                # Mise a jour
                g[neighbor] = tentative_g
                came_from[neighbor] = current
                
                # Calcul de f = g + w * h
                f_n = tentative_g + weight * heuristic(neighbor, goal)
                open_list.push(neighbor, f_n)

                if verbose:
                    print(f"         -> {neighbor} ajoute a OPEN avec f = {tentative_g:.2f} + {weight}*{heuristic(neighbor, goal):.2f} = {f_n:.2f}")

                # Reouverture si dans CLOSED (pour heuristiques non coherentes)
                if neighbor in closed:
                    closed.discard(neighbor)
                    if verbose:
                        print(f"         -> {neighbor} retire de CLOSED (reouverture)")
            else:
                if verbose:
                    print(f"         -> Chemin moins bon (g existant = {old_g:.2f}) - ignore")

        if verbose:
            # Afficher OPEN apres iteration
            open_items = []
            if hasattr(open_list, '_finder'):
                for item, entry in open_list._finder.items():
                    if entry[2] is not getattr(open_list, '_REMOVED', object()):
                        open_items.append((item, round(entry[0], 2)))
            print(f"   OPEN apres iteration : {open_items}")
            print("-"*60 + "\n")

    # Aucun chemin trouve
    log.execution_time = time.perf_counter() - t0
    if verbose:
        print(f"\n>>> AUCUN CHEMIN trouve vers {goal}")
        print("="*60 + "\n")
    return log

