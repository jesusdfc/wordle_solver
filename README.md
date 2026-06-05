# palabra-solver

Optimal theoretical player for [**La Palabra del Día**](https://lapalabradeldia.com/) (Spanish Wordle). Each guess is chosen to **maximize information** about the hidden word, not to guess the answer directly.

The solver treats Wordle as **hypothesis-space reduction**: maintain the set of possible secrets, pick the guess that partitions that set most informatively, then filter using the feedback pattern.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync --dev
```

The default dictionary is `lemario-general-del-espanol.txt` at the project root (~87k Spanish lemmas from the RAE general lexicon).

## Quick start

```bash
# Dictionary stats
uv run palabra stats

# Simulate solving a secret offline
uv run palabra solve abril

# Suggest next guess after previous attempts
# Pattern digits: 0=gray, 1=yellow, 2=green (position order, base-3)
uv run palabra suggest --guess audio02201
```

CLI solve output uses ASCII feedback: `.` gray, `y` yellow, `g` green.

Run tests:

```bash
uv run pytest
```

---

## `words.py` — `WordleWordsHandler`

Loads the raw dictionary and produces **playable Wordle words**.

### What it does

1. Reads one word per line from the `.txt` file.
2. Keeps only entries of a given length (default **5** for classic mode).
3. **Strips accents** (`abacá` → `abaca`) because classic mode ignores tildes.
4. **Rejects** entries with spaces, hyphens, digits, or other symbols (`a-`, `ab aeterno`, `-able`).
5. Keeps Spanish **ñ**.
6. **Deduplicates** after normalization.

### API

```python
from pathlib import Path
from palabra_solver import WordleWordsHandler

handler = WordleWordsHandler("lemario-general-del-espanol.txt", length=5)
words = handler.load().words   # tuple[str, ...]
len(handler)                   # number of valid words
"abril" in handler             # membership check
```

### Design notes

- Returns an immutable `tuple` for fast reuse by the solver.
- `normalize()` is exposed for unit tests and one-off checks.
- The lemario is broader than the game's official word list; some valid solver guesses may not be accepted by the website.

---

## `model.py` — entropy / minimax solver

Implements the **theoretical optimal player** using expected information gain.

### Core idea

Start with all possible secrets **W**. For each candidate guess **g**, simulate feedback against every word in **W** and group them into buckets. Pick **g** that makes those buckets as informative as possible.

### Feedback (`feedback.py`)

Wordle rules (including duplicate letters) are encoded as a base-3 integer:

| Code | Color  |
|------|--------|
| 0    | Gray   |
| 1    | Yellow |
| 2    | Green  |

```python
from palabra_solver import pattern, pattern_to_str

pattern("abril", "abaca")   # int in [0, 243)
pattern_to_str(value)       # "⬛🟨🟩⬛⬛" for debugging
```

### Strategies

| Strategy   | Rule                         | Use case                          |
|------------|------------------------------|-----------------------------------|
| `entropy`  | `argmax H(g)`                | Default; best average performance |
| `minimax`  | `argmin max \|bucket\|`      | Conservative; avoids worst cases  |

```python
from palabra_solver import Solver, Strategy

words = handler.words
solver = Solver(words, strategy=Strategy.ENTROPY)

guess = solver.suggest()
solver.update(guess, feedback_pattern)

# Offline simulation
guesses = solver.solve("abril")
```

### Algorithm loop

```
W ← all valid words
while not solved:
    g ← best_guess(W)           # max entropy or min worst-case
    p ← feedback(secret, g)
    W ← { w ∈ W : pattern(w, g) = p }
```

This is **Bayesian optimal experimental design** without learning: pure combinatorics over the remaining hypothesis space.

---

## How to make it better

### 1. Word-frequency priors

Weight secrets by corpus frequency (e.g. SUBTLEX-ESP). Replace uniform `P(p)` with:

```
P(p | g) = Σ_{w ∈ bucket_p} P(w)
```

Common daily words get higher prior probability; the solver becomes more realistic.

### 2. Separate solution and guess sets

- **W** (solutions): ~2k common words — what the game picks.
- **G** (guesses): full dictionary — allowed guesses including rare words.

Using **G** for guessing while filtering **W** improves opening moves.

### 3. Hard mode

Enforce that greens stay in place and yellow letters reappear in later guesses. Restricts the guess pool each turn.

### 4. Performance

- Cache `pattern(a, b)` with `functools.lru_cache`.
- Precompute opening guess offline.
- Use Numba for partition + entropy over large word lists.

### 5. Benchmark suite

Simulate all secrets; report mean / median / p95 guesses. Compare `entropy` vs `minimax` vs fixed openings (`audio`, `orase`).

### 6. Other game modes

- **Tildes**: `WordleWordsHandler(..., preserve_accents=True, length=6)`.
- **Variable length**: parameterize `length` (already supported).

### 7. Neural guidance (advanced)

Train a model to imitate `argmax_entropy` as a fast heuristic, using the theoretical solver as an oracle — similar in spirit to AlphaZero-style search with a learned policy.

---

## Project layout

```
Wordle/
├── lemario-general-del-espanol.txt
├── pyproject.toml
├── README.md
├── src/palabra_solver/
│   ├── words.py       # WordleWordsHandler
│   ├── feedback.py    # pattern encoding
│   ├── model.py       # Solver, entropy, minimax
│   └── cli.py         # palabra command
└── tests/
    ├── test_words.py
    └── fixtures/
```

## License

Dictionary data: check the terms of the [lemario general del español](https://www.dle.rae.es/) source you used. Solver code: use as you see fit.
