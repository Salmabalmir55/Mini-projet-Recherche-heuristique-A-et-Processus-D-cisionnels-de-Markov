# Recherche Heuristique, A* et Processus Decisionnels de Markov

<div align="center">

**Mini-projet - Master SDIA**  
*Module : Base de l'IA*  

**ENSET Mohammedia - Universite Hassan II de Casablanca**  
*Annee universitaire 2025-2026*

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![NumPy](https://img.shields.io/badge/dependency-numpy-orange.svg)](https://numpy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Realise par : BALMIR Salma**  
*Supervise par : M. MESTARI Mohamed*

</div>

---

## Table des matieres

- [Description](#description)
- [Objectifs](#objectifs)
- [Architecture du projet](#architecture-du-projet)
- [Installation](#installation)
- [Execution](#execution)
- [Execution detaillee et captures decran](#execution-detaillee-et-captures-decran)
- [Resultats](#resultats)
- [Extensions](#extensions)
- [Dependances](#dependances)
- [FAQ et Depannage](#faq-et-depannage)
- [References](#references)

---

## Description

Ce projet explore deux piliers fondamentaux de l'intelligence artificielle :

### Partie 1 - Recherche heuristique sur graphe

Implementation et analyse comparative de trois algorithmes de recherche de chemin optimal :

| Algorithme | Fonction d'evaluation | Caracteristique |
|------------|----------------------|-----------------|
| **Greedy Best-First** | `f(n) = h(n)` | Rapide mais non optimal |
| **UCS** (Uniform-Cost Search) | `f(n) = g(n)` | Optimal mais non guide |
| **A\*** | `f(n) = g(n) + h(n)` | Optimal et efficace (si h admissible) |
| **Weighted A\*** | `f(n) = g(n) + w*h(n)` | Compromis parametrable |

**Concepts cles** : admissibilite, coherence, dominance heuristique, reouverture de CLOSED.

### Partie 2 - Chaine de Markov absorbante

Modelisation du **probleme classique de la ruine du joueur** :

- Etats : fortune du joueur `{0,1,2,3,4,5,6}`
- Etats absorbants : `0` (ruine) et `6` (victoire)
- Calcul analytique complet :
  - Matrice de transition `P`
  - Forme canonique `[I 0 ; R Q]`
  - Matrice fondamentale `N = (I-Q)^(-1)`
  - Probabilites d'absorption `B = N*R`
  - Esperance du temps `t = N*1`
- Validation par **simulation Monte Carlo** (200 000 essais)

---

## Objectifs

- [x] Implementer correctement les algorithmes de recherche avec gestion OPEN/CLOSED
- [x] Analyser l'impact de la qualite des heuristiques sur les performances
- [x] Valider experimentalement les proprietes theoriques (admissibilite, coherence)
- [x] Modeliser et resoudre analytiquement une chaine de Markov absorbante
- [x] Comparer resultats analytiques et simulation Monte Carlo
- [x] Traiter **5 extensions** pour approfondir l'analyse

---

## Architecture du projet

```
project/
|
+-- main.py                  # Point d'entree CLI
|
+-- search/                  # Algorithmes de recherche
|   +-- astar.py             # A* et Weighted A*
|   +-- ucs.py               # Uniform-Cost Search
|   +-- greedy.py            # Greedy Best-First
|   +-- utils.py             # PriorityQueue, logs, generateur
|
+-- markov/                  # Chaines de Markov
|   +-- absorbing_chain.py   # Calculs analytiques (N, B, t)
|   +-- simulation.py        # Monte Carlo (200k essais)
|
+-- experiments/             # Experimentations
|   +-- graphs.py            # Graphe du cours, heuristiques
|   +-- benchmarks.py        # Benchmarks et extensions E1-E5
|
+-- data/                    # Donnees JSON (reproductibilite)
|   +-- graph_cours.json     # Graphe S->G + 3 heuristiques
|   +-- markov_params.json   # Parametres joueur + scenarios
|   +-- benchmark_config.json# Graphes aleatoires + poids w
|
+-- README.md                # Documentation (vous etes ici)
```

---

## Installation

### Prerequis

- Python 3.9 ou superieur
- pip (gestionnaire de paquets)

```bash
# 1. Extraire le ZIP
unzip projet_recherche_heuristique.zip
cd project

# 2. (Optionnel) Creer un environnement virtuel
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Installer l'unique dependance externe
pip install numpy
```

> **Note** : NumPy est utilise uniquement pour l'inversion matricielle `(I-Q)^(-1)` dans
> `absorbing_chain.py`. Tous les autres modules utilisent la bibliotheque standard Python.

---

## Execution

### Lancer l'integralite du projet

```bash
python main.py
```

### Commandes par partie

| Commande | Description |
|----------|-------------|
| `python main.py --part search` | Parties II & III (Greedy, A*, UCS) |
| `python main.py --part search --verbose` | Affichage pas-a-pas de OPEN/CLOSED |
| `python main.py --part benchmark` | Partie IV (benchmark graphes aleatoires) |
| `python main.py --part markov` | Partie V (chaine de Markov, p=0.5 par defaut) |
| `python main.py --part markov --p 0.3` | Probabilite asymetrique |
| `python main.py --part markov --trials 500000` | Augmentation des essais Monte Carlo |
| `python main.py --part extensions` | Extensions E1 (dominance) et E3 (Weighted A*) |
| `python main.py --part all` | Tout executer (defaut) |

### Parametres CLI

| Argument | Type | Defaut | Description |
|----------|------|--------|-------------|
| `--part` | `{search,markov,benchmark,extensions,all}` | `all` | Partie a executer |
| `--verbose` | flag | `False` | Affiche OPEN/CLOSED a chaque etape |
| `--p` | float | `0.5` | Probabilite de gain (Markov) |
| `--trials` | int | `200000` | Nombre d'essais Monte Carlo |
| `--start` | int | `2` | Etat initial pour Markov |

> **Important** : Toujours executer depuis **a l'interieur du dossier `project/`**.

---

## Execution detaillee et captures decran

### Commande recommandee pour visualiser toutes les etapes

```bash
python main.py --part search --verbose
```

Cette commande affiche pour chaque algorithme :
- Le noeud extrait a chaque iteration
- Les valeurs `g(n)`, `h(n)`, `f(n)` en temps reel
- La taille de OPEN apres chaque etape
- Le chemin final et le cout total

---

### Figure 1 -- A* simulation pas-a-pas (`--verbose`)

```bash
python main.py --part search --verbose
```
<img width="768" height="662" alt="image" src="https://github.com/user-attachments/assets/3fffa88e-aadd-4aed-b28c-bb1c22f1ed49" />
<img width="917" height="742" alt="image" src="https://github.com/user-attachments/assets/ba664878-64b5-4462-85ce-448b751342f5" />
<img width="937" height="778" alt="image" src="https://github.com/user-attachments/assets/546e0976-70b2-44f3-9681-d1ae201fc94f" />


---

### Figure 2 -- Greedy et UCS simulation pas-a-pas

```bash
python main.py --part search --verbose
```


<b>Greedy Best-First Search</b>

<img width="640" height="682" alt="image" src="https://github.com/user-attachments/assets/5e25316f-705a-47ce-90ca-2bedbfc978a4" />
<img width="720" height="763" alt="image" src="https://github.com/user-attachments/assets/6e9dbb7d-c98f-43e5-a93c-9f34be341e74" />


<b>UNIFORM-COST SEARCH (UCS)</b>
  
<img width="746" height="817" alt="image" src="https://github.com/user-attachments/assets/4de75a3a-dac6-44d7-8f65-f178979158a0" />
<img width="720" height="822" alt="image" src="https://github.com/user-attachments/assets/e947a222-8627-4750-8e23-24074dfd1b7e" />
<img width="711" height="440" alt="image" src="https://github.com/user-attachments/assets/94701eea-f1f6-4033-bb0f-e021031d0bb8" />

---

### Figure 3 -- Comparaison des algorithmes et etude des heuristiques

```bash
python main.py --part search
```
<img width="1052" height="670" alt="image" src="https://github.com/user-attachments/assets/a07b145d-2f98-4637-8dbd-f7aecbd31f7c" />




---

### Figure 4 -- Benchmark sur graphes aleatoires

```bash
python main.py --part benchmark
```
<img width="957" height="647" alt="image" src="https://github.com/user-attachments/assets/842a8d85-0ca7-4bde-9d09-da62ed4abda2" />


---

### Figure 5 -- Weighted A* (Extension E3)

```bash
python main.py --part extensions
```
<img width="1037" height="563" alt="image" src="https://github.com/user-attachments/assets/0808f70c-c95f-458b-81fc-6616364427d7" />



---

### Figure 6 -- Chaine de Markov : analytique vs Monte Carlo

```bash
python main.py --part markov
```
<img width="1087" height="707" alt="image" src="https://github.com/user-attachments/assets/bc5160ef-7848-49b5-9dd3-e1eb64914b4e" />
<img width="1092" height="752" alt="image" src="https://github.com/user-attachments/assets/02575e16-c8b5-4409-b6f6-170d27de0586" />
<img width="862" height="562" alt="image" src="https://github.com/user-attachments/assets/bb568c5f-ef39-4a54-986c-ef819f02418f" />
<img width="1001" height="532" alt="image" src="https://github.com/user-attachments/assets/19d64b0b-6582-4035-a846-e82884af25c6" />
<img width="1077" height="237" alt="image" src="https://github.com/user-attachments/assets/e32c99a9-567e-45ab-9104-615fe2ddc910" />



---

## Resultats

### Partie II - Simulation sur le graphe du cours (S -> G)

Graphe :
```
S --(1)--> A --(2)--> C --(5)--> G
S --(4)--> B --(1)--> D --(3)--> G
           A --(5)--> D
```

Heuristique admissible & coherente : `h(S)=7, h(A)=6, h(B)=5, h(C)=4, h(D)=2, h(G)=0`

| Algorithme | Chemin trouve | Cout | Noeuds developpes | Optimal ? |
|------------|--------------|------|-------------------|-----------|
| Greedy | S -> B -> D -> G | 8 | 4 | Oui (ici) |
| A* | S -> A -> C -> G | 8 | 5 | Oui |
| UCS | S -> A -> C -> G | 8 | 6 | Oui |

> Greedy peut trouver l'optimal sur certains graphes -- ce n'est pas garanti mathematiquement.

### Partie III - Impact de la qualite de l'heuristique

| Heuristique | Cout | Noeuds | Observation |
|-------------|------|--------|-------------|
| Admissible & coherente | 8 | 5 | Optimal, pas de reouverture |
| Admissible non coherente | 8 | 7 | Optimal mais reouvertures possibles |
| Non admissible | 8 | 4 | Chanceux ici (non garanti) |
| Nulle (UCS) | 8 | 6 | Exploration exhaustive |

### Partie IV - Benchmark sur graphes aleatoires

| Graphe | UCS | Greedy | A* | WA*(w=2) | Greedy optimal ? |
|--------|-----|--------|----|----------|------------------|
| cours (6 noeuds) | 6 | 4 | 5 | 4 | Oui |
| rand_10n_20e | 4 | 5 | 4 | 4 | Oui |
| rand_20n_50e | 15 | 11 | 15 | 15 | Non (18.2 vs 16.4) |
| rand_50n_150e | 45 | 39 | 45 | 45 | Non (28.4 vs 27.6) |
| rand_100n_400e | 96 | 92 | 96 | 96 | Non (23.7 vs 21.6) |

### Weighted A* - Compromis w vs optimalite

| w | Cout trouve | Ratio | Noeuds | Gain |
|---|-------------|-------|--------|------|
| 1.0 | 8.00 | 1.000 | 5 | 0% |
| 1.5 | 8.00 | 1.000 | 4 | 20% |
| 2.0 | 9.00 | 1.125 | 4 | 20% |
| 3.0 | 9.00 | 1.125 | 4 | 40% |
| 5.0 | 8.00 | 1.000 | 4 | 40% |

> La borne theorique `cout <= w x optimal` est toujours respectee.

### Partie V - Chaine de Markov (p = 0.5, depart etat 2)

**Calculs analytiques :**

| Grandeur | Formule | Valeur |
|----------|---------|--------|
| P(ruine \| X0=2) | 1 - i/N | 0.6667 |
| P(victoire \| X0=2) | i/N | 0.3333 |
| E[T \| X0=2] | i*(N-i) | 8.0000 |

**Validation Monte Carlo (200 000 essais) :**

| Resultat | Analytique | Monte Carlo | Ecart |
|----------|------------|-------------|-------|
| P(ruine) | 0.666667 | ~0.6677 | < 0.15% |
| P(victoire) | 0.333333 | ~0.3323 | < 0.15% |
| E[T] | 8.0000 | ~7.987 | < 0.17% |

---

## Extensions

### E1 - Dominance heuristique

| Heuristique | S | A | B | C | D | G | Noeuds (100n) |
|-------------|---|---|---|---|---|---|---------------|
| h haute (dominante) | 7 | 6 | 4 | 4 | 2 | 0 | 92 |
| h basse | 4 | 3 | 2 | 1 | 0 | 0 | 95 |
| h nulle (UCS) | 0 | 0 | 0 | 0 | 0 | 0 | 96 |

> Gain de 4% sur 100 noeuds -- la dominance devient significative sur les grandes instances.

### E2 - Generateur automatique de graphes

```python
# Generation reproductible (seed fixe)
graph, name = generate_random_graph(n_nodes=100, n_edges=400, seed=42)
```

- Garantie de connexite par chaine hamiltonienne
- Couts aleatoires dans [1, 10]
- Reproductible via seed fixe

### E3 - Weighted A* : analyse parametrique

| w | Comportement | Cas d'usage |
|---|-------------|-------------|
| 1 | A* standard | Applications critiques |
| 1.5 | Optimal maintenu, +20% rapide | Compromis ideal |
| 2 | Leger surcout (9 vs 8) | Temps reel modere |
| 3+ | Sous-optimal borne | Jeux video, rapidite |

### E4 - Probabilites asymetriques (p different de 0.5)

| p | P(ruine) | P(victoire) | E[T] | Interpretation |
|---|----------|-------------|------|----------------|
| 0.3 | 0.9723 | 0.0277 | 4.58 | Tres defavorable |
| 0.4 | 0.8797 | 0.1203 | 6.39 | Defavorable |
| 0.5 | 0.6667 | 0.3333 | 8.00 | Equitable |
| 0.6 | 0.3910 | 0.6090 | 8.27 | Favorable |
| 0.7 | 0.1786 | 0.8214 | 7.32 | Tres favorable |

Formule generale : `P(ruine) = (r^i - r^N) / (1 - r^N)` avec `r = (1-p)/p`

### E5 - Sensibilite de E[T] a la fortune initiale

| Etat i | E[T] = i*(6-i) |
|--------|----------------|
| 1 | 5 |
| 2 | 8 |
| 3 | 9 |
| 4 | 8 |
| 5 | 5 |

> Forme parabolique, maximum au centre (i=3), symetrie parfaite pour p=0.5.

---

## Dependances

| Package | Version | Utilisation |
|---------|---------|-------------|
| `numpy` | >= 1.24 | Inversion matricielle (I-Q)^(-1) |
| `heapq` | stdlib | File de priorite O(log n) |
| `random` | stdlib | Generateurs de graphes, Monte Carlo |
| `argparse` | stdlib | Interface en ligne de commande |
| `time` | stdlib | Mesure des performances |
| `json` | stdlib | Chargement des configurations |
| `dataclasses` | stdlib | Structure SearchLog |

```bash
# Installation minimale
pip install numpy
```

---

---

<div align="center">

*Mini-projet realise dans le cadre du Master SDIA*  
*ENSET Mohammedia -- 2025/2026*  
**BALMIR Salma**

</div>
