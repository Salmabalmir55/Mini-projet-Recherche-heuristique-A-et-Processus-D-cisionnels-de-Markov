
from __future__ import annotations
import sys
if hasattr(sys.stdout,"reconfigure") and sys.stdout.encoding and sys.stdout.encoding.lower()!="utf-8":
    sys.stdout.reconfigure(encoding="utf-8",errors="replace")

import json
import os
import numpy as np
from typing import Any, Dict, List, Optional


class AbsorbingMarkovChain:
    """Chaine de Markov absorbante generique sous forme canonique."""

    def __init__(
        self,
        states:            List[Any],
        absorbing_states:  List[Any],
        transition_matrix: np.ndarray,
    ) -> None:
        self.states         = states
        self.absorbing_set  = set(absorbing_states)
        self.absorbing_list = [s for s in states if s in self.absorbing_set]
        self.transient      = [s for s in states if s not in self.absorbing_set]

        idx      = {s: i for i, s in enumerate(states)}
        self.P   = transition_matrix.copy()

        # Forme canonique : absorbants en tete
        canon_order      = self.absorbing_list + self.transient
        canon_idx        = [idx[s] for s in canon_order]
        self.P_canonical = self.P[np.ix_(canon_idx, canon_idx)]

        na     = len(self.absorbing_list)
        self.Q = self.P_canonical[na:, na:]   # transitoire -> transitoire
        self.R = self.P_canonical[na:, :na]   # transitoire -> absorbant

        nt      = len(self.transient)
        self.N  = np.linalg.inv(np.eye(nt) - self.Q)   # (I-Q)^{-1}
        self.B  = self.N @ self.R                        # probabilites d'absorption
        self.t  = self.N @ np.ones(nt)                  # esperance du temps

    # -- Requetes -------------------------------------------------------------

    def absorption_probs(self, start_state: Any) -> Dict[Any, float]:
        if start_state in self.absorbing_set:
            return {start_state: 1.0}
        i = self.transient.index(start_state)
        return {s: float(self.B[i, j]) for j, s in enumerate(self.absorbing_list)}

    def expected_time(self, start_state: Any) -> float:
        if start_state in self.absorbing_set:
            return 0.0
        i = self.transient.index(start_state)
        return float(self.t[i])

    def expected_visits(self, from_state: Any, to_state: Any) -> float:
        if from_state in self.absorbing_set or to_state in self.absorbing_set:
            return 0.0
        i = self.transient.index(from_state)
        j = self.transient.index(to_state)
        return float(self.N[i, j])

    # -- Affichage -------------------------------------------------------------

    def print_summary(self) -> None:
        np.set_printoptions(precision=4, suppress=True, linewidth=120)
        print("\n" + "=" * 60)
        print("  CHAINE DE MARKOV ABSORBANTE - RESULTATS ANALYTIQUES")
        print("=" * 60)
        print(f"  Etats        : {self.states}")
        print(f"  Absorbants   : {self.absorbing_list}")
        print(f"  Transitoires : {self.transient}")

        _print_matrix(self.P,          self.states,                        self.states,         "Matrice P complete")
        _print_matrix(self.P_canonical, self.absorbing_list+self.transient, self.absorbing_list+self.transient, "Forme canonique [I 0 ; R Q]")
        _print_matrix(self.Q, self.transient, self.transient,              "Sous-matrice Q  (transitoire -> transitoire)")
        _print_matrix(self.R, self.transient, self.absorbing_list,         "Sous-matrice R  (transitoire -> absorbant)")
        _print_matrix(self.N, self.transient, self.transient,              "Matrice fondamentale N = (IQ)^-")
        _print_matrix(self.B, self.transient, self.absorbing_list,         "Probabilites d'absorption B = N.R")

        print("\n-- Esperance du temps avant absorption  t = N.1 ------------")
        for s, ti in zip(self.transient, self.t):
            print(f"   E[T | X={s}] = {ti:.4f} etapes")
        print()


def _print_matrix(M, row_labels, col_labels, title=""):
    if title:
        print(f"\n-- {title} {'-'*max(0,44-len(title))}")
    print("        " + "".join(f"{str(c):>9}" for c in col_labels))
    for i, rl in enumerate(row_labels):
        print(f"  {str(rl):>4}  |" + "".join(f"{M[i,j]:>9.4f}" for j in range(M.shape[1])))


# -- Constructeur pour le probleme du joueur -----------------------------------

def build_gambler_chain(p: float = 0.5, max_fortune: int = 6) -> AbsorbingMarkovChain:

    n = max_fortune + 1
    P = np.zeros((n, n))
    P[0, 0] = 1.0
    P[max_fortune, max_fortune] = 1.0
    for i in range(1, max_fortune):
        P[i, i + 1] = p
        P[i, i - 1] = 1.0 - p
    return AbsorbingMarkovChain(
        states            = list(range(n)),
        absorbing_states  = [0, max_fortune],
        transition_matrix = P,
    )


def load_markov_params(data_dir: str = None) -> dict:
    """Charge data/markov_params.json et retourne le dictionnaire."""
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "data")
    path = os.path.join(data_dir, "markov_params.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
