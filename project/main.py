
# -*- coding: utf-8 -*-

"""
Mini-projet - Recherche Heuristique, A* et Processus Décisionnels de Markov
Master SDIA - ENSET Mohammedia
Auteur: BALMIR Salma
Année: 2025-2026
"""

from __future__ import annotations

import sys
import os
import argparse

# Configuration des chemins d'import
_ROOT = os.path.dirname(os.path.abspath(__file__))
for _pkg in ("search", "markov", "experiments"):
    _p = os.path.join(_ROOT, _pkg)
    if _p not in sys.path:
        sys.path.insert(0, _p)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Imports des modules du projet
from benchmarks import (
    run_step_by_step,
    run_heuristic_study,
    run_full_benchmark,
    run_markov,
    run_dominance_study,
    run_weighted_astar_study,
)
from graphs import SOURCE_COURS, GOAL_COURS, GRAPH_COURS, H_ADMISSIBLE_COHERENTE
from utils import make_dict_heuristic, print_table
from astar import astar
from greedy import greedy_best_first
from ucs import ucs


def section_intro() -> None:
    """Affiche l'introduction avec le graphe du cours."""
    print("""
Graphe du cours [data/graph_cours.json] :
  S --(1)--> A --(2)--> C --(5)--> G
  S --(4)--> B --(1)--> D --(3)--> G
             A --(5)--> D

Heuristique admissible & coherente :
  h(S)=7, h(A)=6, h(B)=5, h(C)=4, h(D)=2, h(G)=0

Solution optimale A* : S -> A -> C -> G   cout = 8
""")


def section_extensions() -> None:
    """Affiche les extensions E1 et E3."""
    print("\n" + "=" * 64)
    print("  EXTENSIONS - E1 (Dominance) & E3 (Weighted A*)")
    print("=" * 64)
    run_dominance_study()
    run_weighted_astar_study()


def run_detailed_search() -> None:
    """
    Execute les algorithmes de recherche avec affichage detaille.
    Affiche chaque iteration avec OPEN, CLOSED et les calculs.
    """
    print("\n" + "=" * 60)
    print("  SIMULATION DETAILLEE DES ALGORITHMES DE RECHERCHE")
    print("=" * 60)
    
    h = make_dict_heuristic(H_ADMISSIBLE_COHERENTE)
    
    # 1. Greedy Best-First Search
    print("\n" + "=" * 60)
    print("  GREEDY BEST-FIRST SEARCH - Depart: S -> But: G")
    print("=" * 60)
    greedy_best_first(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, verbose=True)
    
    # 2. A* Search
    print("\n" + "=" * 60)
    print("  A* - RECHERCHE HEURISTIQUE")
    print("=" * 60)
    astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, weight=1.0, verbose=True)
    
    # 3. UCS
    print("\n" + "=" * 60)
    print("  UNIFORM-COST SEARCH (UCS)")
    print("=" * 60)
    ucs(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, verbose=True)
    
    # 4. Weighted A* (w=2)
    print("\n" + "=" * 60)
    print("  WEIGHTED A* (w=2.0)")
    print("=" * 60)
    astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, weight=2.0, verbose=True)


def run_detailed_astar_only() -> None:
    """Execute uniquement A* avec affichage detaille."""
    print("\n" + "=" * 60)
    print("  A* - RECHERCHE HEURISTIQUE")
    print("=" * 60)
    
    h = make_dict_heuristic(H_ADMISSIBLE_COHERENTE)
    result = astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, weight=1.0, verbose=True)
    print("\n" + "=" * 60)
    print("  RESUME")
    print("=" * 60)
    print(result.summary())


def run_detailed_greedy_only() -> None:
    """Execute uniquement Greedy avec affichage detaille."""
    print("\n" + "=" * 60)
    print("  GREEDY BEST-FIRST SEARCH")
    print("=" * 60)
    
    h = make_dict_heuristic(H_ADMISSIBLE_COHERENTE)
    result = greedy_best_first(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, verbose=True)
    print("\n" + "=" * 60)
    print("  RESUME")
    print("=" * 60)
    print(result.summary())


def run_detailed_ucs_only() -> None:
    """Execute uniquement UCS avec affichage detaille."""
    print("\n" + "=" * 60)
    print("  UNIFORM-COST SEARCH (UCS)")
    print("=" * 60)
    
    result = ucs(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, verbose=True)
    print("\n" + "=" * 60)
    print("  RESUME")
    print("=" * 60)
    print(result.summary())


def run_detailed_weighted_astar(w: float = 2.0) -> None:
    """Execute Weighted A* avec affichage detaille."""
    print(f"\n" + "=" * 60)
    print(f"  WEIGHTED A* (w={w})")
    print("=" * 60)
    
    h = make_dict_heuristic(H_ADMISSIBLE_COHERENTE)
    result = astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, weight=w, verbose=True)
    print("\n" + "=" * 60)
    print("  RESUME")
    print("=" * 60)
    print(result.summary())


def main() -> None:
    """Point d'entree principal du programme."""
    parser = argparse.ArgumentParser(
        description="Mini-projet - Recherche Heuristique, A* et MDP",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--part",
        choices=[
            "search", "markov", "benchmark", "extensions", "all",
            "detailed", "astar", "greedy", "ucs", "wastar"
        ],
        default="all",
        help="""Partie a executer :
  search     -> Parties II & III (sans details)
  benchmark  -> Partie IV
  markov     -> Partie V + E4, E5
  extensions -> E1 + E3
  detailed   -> Tous les algorithmes avec details
  astar      -> A* detaille uniquement
  greedy     -> Greedy detaille uniquement
  ucs        -> UCS detaille uniquement
  wastar     -> Weighted A* detaille (utiliser --weight)
  all        -> tout (defaut)""",
    )
    parser.add_argument("--verbose", action="store_true",
                        help="Affichage pas-a-pas des algorithmes")
    parser.add_argument("--p", type=float, default=None,
                        help="Probabilite p (Markov) - defaut: valeur JSON")
    parser.add_argument("--trials", type=int, default=None,
                        help="Essais Monte Carlo - defaut: valeur JSON")
    parser.add_argument("--start", type=int, default=2,
                        help="Etat initial Markov (defaut 2)")
    parser.add_argument("--weight", type=float, default=2.0,
                        help="Poids w pour Weighted A* (defaut 2.0)")

    args = parser.parse_args()

    # Execution
    section_intro()

    # Cas d'affichage detaille
    if args.part == "detailed":
        run_detailed_search()
        
    elif args.part == "astar":
        run_detailed_astar_only()
        
    elif args.part == "greedy":
        run_detailed_greedy_only()
        
    elif args.part == "ucs":
        run_detailed_ucs_only()
        
    elif args.part == "wastar":
        run_detailed_weighted_astar(args.weight)
        
    # Cas standards
    else:
        if args.part in ("search", "all"):
            run_step_by_step(verbose=args.verbose)
            run_heuristic_study()

        if args.part in ("benchmark", "all"):
            run_full_benchmark()

        if args.part in ("markov", "all"):
            run_markov(p=args.p, start_state=args.start, n_trials=args.trials)

        if args.part in ("extensions", "all"):
            section_extensions()

    print("\nExecution terminee avec succes.\n")


if __name__ == "__main__":
    main()