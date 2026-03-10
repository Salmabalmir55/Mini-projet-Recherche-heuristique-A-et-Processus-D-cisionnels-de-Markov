# Recherche Heuristique, A\* et Processus Décisionnels de Markov

> Mini-projet  – **Master SDIA** – Module : Base de l'IA  
> ENSET Mohammedia – Université Hassan II de Casablanca – 2025/2026  
> Réalisé par : **BALMIR Salma** | Supervisé par : **M. MESTARI Mohamed**

---

## Description

Ce projet implémente et compare trois algorithmes de recherche de chemin sur graphe pondéré, puis modélise le problème de la ruine du joueur par une chaîne de Markov absorbante.

**Partie 1 – Recherche heuristique**
- Greedy Best-First Search, Uniform-Cost Search (UCS) et A\*
- Étude de l'impact de l'admissibilité et de la cohérence de l'heuristique
- Weighted A\* : compromis w vs optimalité
- Benchmark sur graphes aléatoires de taille croissante

**Partie 2 – Chaîne de Markov absorbante**
- Construction de P (7×7), forme canonique, N = (I-Q)⁻¹
- Probabilités d'absorption B = N·R et espérance du temps t = N·1
- Validation Monte Carlo (200 000 essais, seed = 42)
- Extensions : p asymétrique, sensibilité de E[T]

---

## Installation

**Prérequis** : Python 3.9 ou supérieur

```bash
# 1. Cloner le dépôt
git clone https://github.com/<username>/recherche-heuristique-markov.git
cd recherche-heuristique-markov/project

# 2. Installer la seule dépendance externe
pip install numpy
```

> NumPy est utilisé uniquement pour l'inversion matricielle `(I-Q)⁻¹` dans `markov/absorbing_chain.py`.  
> Tous les autres modules utilisent la bibliothèque standard Python.

---

## Exécution

### Lancer tout le projet

```bash
python main.py
```

### Commandes par partie

```bash
# Parties II & III – Simulation Greedy, A*, UCS sur le graphe du cours
python main.py --part search

# Affichage pas-à-pas de OPEN/CLOSED à chaque itération
python main.py --part search --verbose

# Partie IV – Benchmark sur graphes aléatoires
python main.py --part benchmark

# Partie V – Chaîne de Markov (p = 0.5 par défaut)
python main.py --part markov

# Changer la probabilité de gain
python main.py --part markov --p 0.3

# Augmenter le nombre d'essais Monte Carlo
python main.py --part markov --trials 500000

# Extensions E1 (dominance) et E3 (Weighted A*)
python main.py --part extensions
```

### Référence des arguments CLI

| Argument | Valeurs | Défaut | Description |
|---|---|---|---|
| `--part` | `search` `markov` `benchmark` `extensions` `all` | `all` | Partie à exécuter |
| `--verbose` | — | `False` | Affichage pas-à-pas OPEN/CLOSED |
| `--p` | `0.0` à `1.0` | `0.5` | Probabilité de gain (Markov) |
| `--trials` | entier | `200000` | Nombre d'essais Monte Carlo |

---

## Organisation du projet

```
project/
│
├── main.py                        # Point d'entrée CLI
│
├── search/                        # Algorithmes de recherche sur graphe
│   ├── __init__.py
│   ├── astar.py                   # A* et Weighted A* — f(n) = g(n) + w·h(n)
│   ├── ucs.py                     # Uniform-Cost Search — f(n) = g(n)
│   ├── greedy.py                  # Greedy Best-First — f(n) = h(n)
│   └── utils.py                   # PriorityQueue (lazy deletion), SearchLog, générateur
│
├── markov/                        # Chaînes de Markov absorbantes
│   ├── __init__.py
│   ├── absorbing_chain.py         # N = (I-Q)⁻¹, B = N·R, t = N·1
│   └── simulation.py              # Monte Carlo et comparaison analytique/empirique
│
├── experiments/                   # Expérimentations et benchmarks
│   ├── __init__.py
│   ├── graphs.py                  # Graphe du cours, heuristiques h1/h2/h3
│   └── benchmarks.py              # Comparaisons, extensions E1–E5
│
├── data/                          # Paramètres JSON (reproductibilité)
│   ├── graph_cours.json
│   ├── markov_params.json
│   └── benchmark_config.json
│
└── README.md
```

### Rôle de chaque module

| Fichier | Responsabilité |
|---|---|
| `search/astar.py` |  A\* avec gestion OPEN/CLOSED, réouverture CLOSED si h non cohérente, Weighted A\* |
| `search/ucs.py` |  Uniform-Cost Search garanti optimal |
| `search/greedy.py` | Greedy Best-First Search |
| `search/utils.py` | File de priorité O(log n), SearchLog, générateur de graphes (seed) |
| `markov/absorbing_chain.py` | Calcul analytique complet de N, B, t |
| `markov/simulation.py` |  Monte Carlo, 200 000 essais |
| `experiments/graphs.py` |  Graphe du cours, trois jeux d'heuristiques |
| `experiments/benchmarks.py` |  Étude comparative et extensions E1–E5 |
| `main.py` |  Interface CLI, orchestration des sections |

---

## Résultats principaux

### Recherche sur le graphe du cours (S → G)

| Algorithme | Chemin | Coût | Nœuds développés | Optimal |
|---|---|---|---|---|
| Greedy | S→B→D→G | 8 | 4 | Oui (ici) |
| A\* | S→A→C→G | 8 | 5 | Oui ✓ |
| UCS | S→A→C→G | 8 | 6 | Oui ✓ |

> Greedy peut trouver l'optimal sur certains graphes — ce n'est pas garanti.  
> Sur 100 nœuds, Greedy produit un chemin de coût 23.7 vs optimal 21.6 (ratio 9.7%).

### Weighted A\* — Compromis w vs optimalité

| w | Coût trouvé | Ratio | Nœuds dév. | Gain |
|---|---|---|---|---|
| 1.0 | 8 | 1.000 | 5 | 0% |
| 1.5 | 8 | 1.000 | 4 | 20% |
| 2.0 | 9 | 1.125 | 4 | 20% |
| 3.0 | 12 | 1.500 | 3 | 40% |

Borne garantie : `coût_trouvé ≤ w × coût_optimal`

### Chaîne de Markov (p = 0.5, départ état 2)

| Résultat | Analytique | Monte Carlo | Écart |
|---|---|---|---|
| P(ruine \| X₀=2) | 0.666667 | 0.667630 | < 0.1% |
| P(victoire \| X₀=2) | 0.333333 | 0.332370 | < 0.1% |
| E[T \| X₀=2] | 8.0000 | 7.9867 | < 0.2% |

Formule analytique (p = ½) : `P(ruine|X₀=i) = 1 − i/N` et `E[T|X₀=i] = i×(N−i)`

---

## Dépendances

| Package | Version | Usage |
|---|---|---|
| `numpy` | ≥ 1.24 | Inversion matricielle `(I-Q)⁻¹` |
| `heapq` | stdlib | File de priorité dans `utils.py` |
| `random` | stdlib | Générateur de graphes et Monte Carlo |
| `argparse` | stdlib | Interface CLI |
| `time` | stdlib | Mesure du temps d'exécution |

---

## Note Windows

Si vous rencontrez une erreur `UnicodeEncodeError` (encodage cp1252), le `main.py` intègre un correctif automatique :

```python
import io, sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
```

Ou lancez avec la variable d'environnement :
```powershell
$env:PYTHONUTF8 = "1"
python main.py
```

---

