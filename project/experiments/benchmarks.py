
from __future__ import annotations
import sys, os, json

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "search"),
           os.path.join(_ROOT, "markov"),
           os.path.join(_ROOT, "experiments")):
    if _p not in sys.path: sys.path.insert(0, _p)
if _ROOT not in sys.path: sys.path.insert(0, _ROOT)

from typing import List

from astar  import astar
from ucs    import ucs
from greedy import greedy_best_first
from utils  import SearchLog, zero_heuristic, make_dict_heuristic, print_table

from absorbing_chain import build_gambler_chain, load_markov_params
from simulation      import compare_analytical_simulation

from graphs import (
    GRAPH_COURS, SOURCE_COURS, GOAL_COURS, OPTIMAL_SOLUTION,
    H_ADMISSIBLE_COHERENTE, H_ADMISSIBLE_NON_COHERENTE, H_NON_ADMISSIBLE,
    get_benchmark_graphs, get_weighted_astar_weights,
)

_DATA_DIR = os.path.join(_ROOT, "data")


# ============================================================
#  Utilitaire
# ============================================================

def print_comparison_table(logs: List[SearchLog]) -> None:
    rows = [{
        "Algorithme":  log.algorithm,
        "Cout":        f"{log.final_cost:.2f}" if log.final_cost < float("inf") else "inf",
        "Noeuds dev.": log.nodes_expanded,
        "Chemin":      " -> ".join(str(n) for n in log.path) if log.path else "--",
        "Temps(ms)":   f"{log.execution_time * 1000:.3f}",
    } for log in logs]
    print_table(rows, "Comparaison des algorithmes")


# ============================================================
#  Partie II - Simulation pas-a-pas
# ============================================================

def run_step_by_step(verbose: bool = True) -> None:
    print("\n" + "=" * 64)
    print("  PARTIE II - Simulation pas-a-pas (S -> G)")
    print("=" * 64)
    h_ac = make_dict_heuristic(H_ADMISSIBLE_COHERENTE)

    print("\n>> Greedy Best-First Search\n" + "-" * 44)
    log_g = greedy_best_first(GRAPH_COURS, SOURCE_COURS, GOAL_COURS,
                              h_ac, graph_name="cours", verbose=verbose)
    print(log_g.summary())

    print("\n>> A* (w=1) - reproduit le tableau du cours\n" + "-" * 44)
    log_a = astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS,
                  h_ac, weight=1.0, graph_name="cours", verbose=verbose)
    print(log_a.summary())

    # Verification contre la solution attendue du JSON
    expected = OPTIMAL_SOLUTION.get("path", [])
    expected_cost = OPTIMAL_SOLUTION.get("cost", 8)
    ok_path = log_a.path == expected
    ok_cost = abs(log_a.final_cost - expected_cost) < 1e-9
    print(f"\n  Verification solution cours :")
    print(f"    Chemin attendu  : {' -> '.join(expected)}  -> {'[OK]' if ok_path else '[ERREUR]'}")
    print(f"    Cout attendu    : {expected_cost}             -> {'[OK]' if ok_cost else '[ERREUR]'}")

    print("\n>> UCS\n" + "-" * 44)
    log_u = ucs(GRAPH_COURS, SOURCE_COURS, GOAL_COURS,
                graph_name="cours", verbose=verbose)
    print(log_u.summary())

    print_comparison_table([log_u, log_g, log_a])

    print(f"""

   {log_g.nodes_expanded} noeuds, cout={log_g.final_cost:.1f}
   {log_a.nodes_expanded} noeuds, cout={log_a.final_cost:.1f} [OK]
   {log_u.nodes_expanded} noeuds, cout={log_u.final_cost:.1f}
  
""")


# ============================================================
#  Partie III - Etude des heuristiques
# ============================================================

def run_heuristic_study() -> None:
    """
    Compare A* avec les 3 heuristiques de graph_cours.json + nulle.
    """
    print("\n" + "=" * 64)
    print("  PARTIE III - Etude des heuristiques")
    print("=" * 64)

    cases = [
        ("Admissible & coherente   [cours]", make_dict_heuristic(H_ADMISSIBLE_COHERENTE)),
        ("Admissible, non coherente",         make_dict_heuristic(H_ADMISSIBLE_NON_COHERENTE)),
        ("Non admissible",                    make_dict_heuristic(H_NON_ADMISSIBLE)),
        ("Nulle (= UCS)",                     zero_heuristic),
    ]
    rows = []
    for label, h in cases:
        log = astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, graph_name="cours")
        rows.append({
            "Heuristique": label,
            "Cout":        f"{log.final_cost:.2f}" if log.final_cost < float("inf") else "inf",
            "Noeuds dev.": log.nodes_expanded,
            "Chemin":      " -> ".join(log.path),
        })
    print_table(rows, "Impact de la qualite de l'heuristique sur A*")



# ============================================================
#  Partie IV - Benchmark de complexite
# ============================================================

def run_full_benchmark() -> None:
    """
    Benchmark UCS, Greedy, A*, WA*(w=2) sur tous les graphes
    definis dans benchmark_config.json.
    """
    print("\n" + "=" * 64)
    print("  PARTIE IV - Benchmark de complexite experimentale")
    print("=" * 64)

    all_rows = []
    for graph, name, start, goal in get_benchmark_graphs():
        h = make_dict_heuristic(H_ADMISSIBLE_COHERENTE) if name == "cours" else zero_heuristic
        for log in [
            ucs(graph, start, goal, graph_name=name),
            greedy_best_first(graph, start, goal, h, graph_name=name),
            astar(graph, start, goal, h, weight=1.0, graph_name=name),
            astar(graph, start, goal, h, weight=2.0, graph_name=name),
        ]:
            all_rows.append({
                "Graphe":    name,
                "Algo":      log.algorithm,
                "Noeuds":    log.nodes_expanded,
                "Cout":      f"{log.final_cost:.2f}" if log.final_cost < float("inf") else "inf",
                "Temps(ms)": f"{log.execution_time * 1000:.4f}",
            })

    print_table(all_rows, "Benchmark global - tous graphes & algorithmes")



# ============================================================
#  Extensions E1 et E3
# ============================================================

def run_dominance_study() -> None:
    """Extension E1 - Dominance heuristique."""
    h_high = make_dict_heuristic(H_ADMISSIBLE_COHERENTE)
    h_low  = make_dict_heuristic({k: max(0.0, v - 3) for k, v in H_ADMISSIBLE_COHERENTE.items()})

    rows = []
    for label, h in [("h haute (dominante)", h_high),
                     ("h basse",             h_low),
                     ("h nulle",             zero_heuristic)]:
        log = astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h, graph_name="cours")
        rows.append({
            "Heuristique": label,
            "Noeuds dev.": log.nodes_expanded,
            "Cout":        f"{log.final_cost:.2f}",
        })
    print_table(rows, "E1 - Dominance heuristique")


def run_weighted_astar_study() -> None:
    """Extension E3 - Weighted A* : poids w depuis benchmark_config.json."""
    h_ac     = make_dict_heuristic(H_ADMISSIBLE_COHERENTE)
    opt_cost = astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h_ac, weight=1.0).final_cost
    weights  = get_weighted_astar_weights()

    rows = []
    for w in weights:
        log   = astar(GRAPH_COURS, SOURCE_COURS, GOAL_COURS, h_ac, weight=w, graph_name="cours")
        ratio = log.final_cost / opt_cost if opt_cost > 0 else float("nan")
        rows.append({
            "w":          w,
            "Cout":       f"{log.final_cost:.2f}",
            "Ratio/opt.": f"{ratio:.3f}",
            "Noeuds dev.": log.nodes_expanded,
            "Temps(ms)":  f"{log.execution_time * 1000:.3f}",
        })
    print_table(rows, "E3 - Weighted A* : w vs optimalite")


# ============================================================
#  Partie V - Chaine de Markov absorbante
# ============================================================

def run_markov(p: float = None, start_state: int = 2, n_trials: int = None) -> None:
    """
    Partie V + Extensions E4, E5.
    Parametres lus depuis data/markov_params.json.
    """
    params = load_markov_params(_DATA_DIR)

    if p        is None: p        = params["default_p"]
    if n_trials is None: n_trials = params["monte_carlo"]["n_trials"]
    seed = params["monte_carlo"]["seed"]

    print("\n" + "=" * 64)
    print(f"  PARTIE V - Chaine de Markov absorbante  (p={p})")
    print("=" * 64)

    chain = build_gambler_chain(p=p, max_fortune=6)
    chain.print_summary()

    # Resultats analytiques
    print(f"\n-- Resultats analytiques depuis l'etat {start_state} --")
    probs = chain.absorption_probs(start_state)
    for abs_s, prob in sorted(probs.items()):
        label = "ruine (0)" if abs_s == 0 else "victoire (6)"
        print(f"   P(absorption en {abs_s} | X0={start_state}) = {prob:.6f}  [{label}]")
    et = chain.expected_time(start_state)
    print(f"   E[T | X0={start_state}] = {et:.4f} etapes")

    if abs(p - 0.5) < 1e-9:
        ana = params.get("analytical_results_p05", {})
        print(f"\n   Verif. formule (p=1/2) : P(ruine|i={start_state}) = 1-i/N = {1-start_state/6:.6f}")
        print(f"   Formule E[T|i={start_state}]  = i*(N-i) = {start_state*(6-start_state):.1f}")
        if "formula_verification" in ana:
            print(f"   JSON confirme : {ana['formula_verification']}")

    # Validation Monte Carlo
    compare_analytical_simulation(chain, start_state, p, 6,
                                  n_trials=n_trials, seed=seed)

    # Extension E4 : scenarios depuis markov_params.json
    rows_e4 = []
    for scenario in params["scenarios"]:
        p_val = scenario["p"]
        c  = build_gambler_chain(p=p_val, max_fortune=6)
        pr = c.absorption_probs(start_state)
        rows_e4.append({
            "p":           p_val,
            "Scenario":    scenario["label"],
            "P(ruine)":    f"{pr.get(0, 0):.6f}",
            "P(victoire)": f"{pr.get(6, 0):.6f}",
            "E[T]":        f"{c.expected_time(start_state):.4f}",
        })
    print_table(rows_e4, "E4 - Scenarios depuis markov_params.json")

    # Extension E5 : E[T] vs fortune initiale
    chain_sym = build_gambler_chain(p=0.5, max_fortune=6)
    rows_e5   = [{"Etat i": s, "E[T | X0=i]": f"{chain_sym.expected_time(s):.4f}"}
                 for s in chain_sym.transient]
    print_table(rows_e5, "E5 - E[T] vs fortune initiale (p=0.5)")
