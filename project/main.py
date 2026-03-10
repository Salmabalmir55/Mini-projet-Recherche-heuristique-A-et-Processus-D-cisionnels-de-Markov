
import argparse
import sys
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
for _pkg in ("search", "markov", "experiments"):
    _p = os.path.join(_ROOT, _pkg)
    if _p not in sys.path:
        sys.path.insert(0, _p)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from benchmarks import (
    run_step_by_step,
    run_heuristic_study,
    run_full_benchmark,
    run_markov,
    run_dominance_study,
    run_weighted_astar_study,
)
from graphs import SOURCE_COURS, GOAL_COURS


def section_intro() -> None:
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
    print("\n" + "=" * 64)
    print("  EXTENSIONS - E1 (Dominance) & E3 (Weighted A*)")
    print("=" * 64)
    run_dominance_study()
    run_weighted_astar_study()



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mini-projet - Recherche Heuristique, A* et MDP",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--part",
        choices=["search", "markov", "benchmark", "extensions", "all"],
        default="all",
        help=(
            "Partie a executer :\n"
            "  search     -> Parties II & III\n"
            "  benchmark  -> Partie IV\n"
            "  markov     -> Partie V + E4, E5\n"
            "  extensions -> E1 + E3\n"
            "  all        -> tout (defaut)"
        ),
    )
    parser.add_argument("--verbose", action="store_true",
                        help="Affichage pas-a-pas des algorithmes")
    parser.add_argument("--p",      type=float, default=None,
                        help="Probabilite p (Markov) - defaut : valeur JSON")
    parser.add_argument("--trials", type=int,   default=None,
                        help="Essais Monte Carlo - defaut : valeur JSON")
    parser.add_argument("--start",  type=int,   default=2,
                        help="Etat initial Markov (defaut 2)")
    args = parser.parse_args()

    section_intro()

    if args.part in ("search", "all"):
        run_step_by_step(verbose=args.verbose)
        run_heuristic_study()

    if args.part in ("benchmark", "all"):
        run_full_benchmark()

    if args.part in ("markov", "all"):
        run_markov(p=args.p, start_state=args.start, n_trials=args.trials)

    if args.part in ("extensions", "all"):
        section_extensions()

    print("\n[OK]  Execution terminee avec succes.\n")


if __name__ == "__main__":
    main()
