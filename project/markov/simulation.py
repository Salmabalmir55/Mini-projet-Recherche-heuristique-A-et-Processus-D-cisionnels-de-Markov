
from __future__ import annotations
import sys
if hasattr(sys.stdout,"reconfigure") and sys.stdout.encoding and sys.stdout.encoding.lower()!="utf-8":
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "markov"),):
    if _p not in sys.path: sys.path.insert(0, _p)

import random
from typing import Dict, List

import numpy as np
from absorbing_chain import AbsorbingMarkovChain


def simulate_gambler(
    p:           float,
    start:       int,
    max_fortune: int,
    n_trials:    int = 100_000,
    seed:        int = 42,
) -> Dict:

    rng           = random.Random(seed)
    absorb_counts = {0: 0, max_fortune: 0}
    times:        List[int] = []

    for _ in range(n_trials):
        state = start
        steps = 0
        while state not in (0, max_fortune):
            state = (state + 1) if rng.random() < p else (state - 1)
            steps += 1
        absorb_counts[state] = absorb_counts.get(state, 0) + 1
        times.append(steps)

    arr = np.array(times, dtype=float)
    return {
        "absorb_probs": {s: c / n_trials for s, c in absorb_counts.items()},
        "mean_time":    float(arr.mean()),
        "std_time":     float(arr.std()),
        "n_trials":     n_trials,
    }


def compare_analytical_simulation(
    chain:       AbsorbingMarkovChain,
    start_state: int,
    p:           float,
    max_fortune: int,
    n_trials:    int = 200_000,
    seed:        int = 42,
) -> None:
    """Affiche comparaison analytique vs Monte Carlo."""
    ana_probs = chain.absorption_probs(start_state)
    ana_time  = chain.expected_time(start_state)
    sim       = simulate_gambler(p, start_state, max_fortune, n_trials, seed)

    print("\n" + "=" * 62)
    print("  COMPARAISON ANALYTIQUE vs MONTE CARLO")
    print(f"  Depart : etat {start_state}  |  p={p}  |  {n_trials:,} essais")
    print("=" * 62)
    print(f"\n  {'Etat':>6}  {'Analytique':>12}  {'Monte Carlo':>12}  {'|Ecart|':>10}")
    print("  " + "-" * 48)
    for abs_s in sorted(ana_probs):
        ana  = ana_probs[abs_s]
        emp  = sim["absorb_probs"].get(abs_s, 0.0)
        print(f"  {abs_s:>6}  {ana:>12.6f}  {emp:>12.6f}  {abs(ana-emp):>10.6f}")

    emp_t = sim["mean_time"]
    print(f"\n  {'E[T]':>6}  {ana_time:>12.4f}  {emp_t:>12.4f}  {abs(ana_time-emp_t):>10.4f}")
    print(f"  {'std':>6}  {'-':>12}  {sim['std_time']:>12.4f}")
    print()
