# palabra-solver

Optimal theoretical player for [**La Palabra del Día**](https://lapalabradeldia.com/) (Spanish Wordle). The codebase is structured as a **POMDP**: a hidden secret word, partial observations (color feedback), and an agent that maintains a **belief state** over possible secrets.

Each guess is chosen to **maximize information** about the hidden word, not to guess the answer directly.

## Architecture

See [`diagram.d2`](diagram.d2) for a full component diagram. Render with:

```bash
d2 --layout elk diagram.d2 diagram.svg
```

```
data.py   → WordleWordsHandler   action space (dictionary)
env.py     → WordleEnv            environment (secret, step, reward)
belief.py  → BeliefState          POMDP belief b(s) over secrets
agent.py   → WordleAgent          policy π(b) → next guess
```

| Module | Class | RL role |
|--------|-------|---------|
| `data.py` | `WordleWordsHandler` | Action space / dictionary |
| `env.py` | `WordleEnv` | Environment (hidden state + dynamics) |
| `belief.py` | `BeliefState` | Belief over hidden state |
| `agent.py` | `WordleAgent` | Policy (entropy / minimax) |

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-extras
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

Run tests and lint:

```bash
uv run pytest
make checks
```

---

## `data.py` — `WordleWordsHandler`

Loads the raw dictionary and produces **playable Wordle words**.

1. Reads one word per line from the `.txt` file.
2. Keeps only entries of a given length (default **5** for classic mode).
3. **Strips accents** (`abacá` → `abaca`) because classic mode ignores tildes.
4. **Rejects** entries with spaces, hyphens, digits, or other symbols.
5. Keeps Spanish **ñ** and **deduplicates** after normalization.

```python
from palabra_solver import WordleWordsHandler

handler = WordleWordsHandler("lemario-general-del-espanol.txt", length=5)
words = handler.load().words
```

---

## `env.py` — `WordleEnv`

Stateful game simulator. Owns the **hidden secret** and the **observation function** (Wordle color rules).

| Method | RL concept |
|--------|------------|
| `reset(secret=...)` | Start episode, sample or fix secret |
| `step(guess)` | Apply action → `(observation, reward, done, info)` |
| `pattern(secret, guess)` | Transition / observation dynamics |

```python
from palabra_solver import WordleEnv

env = WordleEnv(words)
env.reset(secret="abril")
obs, reward, done, info = env.step("abaca")
# info["pattern"] → base-3 feedback integer
```

Feedback codes: `GRAY=0`, `YELLOW=1`, `GREEN=2`. Reward: `+1` win, `-1` loss, `0` otherwise.

---

## `belief.py` — `BeliefState`

Tracks the agent's **posterior** over possible secrets. After each observation, inconsistent words are removed.

```python
from palabra_solver import BeliefState

belief = BeliefState(words)
belief.update("abaca", feedback_pattern)
print(belief.candidates)   # remaining secrets
print(belief.is_solved())  # True when one candidate left
```

This is the standard POMDP **belief state** `b(s)`: a uniform distribution over the remaining candidate set.

---

## `agent.py` — `WordleAgent`

Policy that maps belief → action. Implements two strategies:

| Strategy | Rule | Use case |
|----------|------|----------|
| `entropy` | `argmax H(g)` | Default; best average performance |
| `minimax` | `argmin max \|bucket\|` | Conservative; avoids worst cases |

```python
from palabra_solver import WordleAgent, Strategy

agent = WordleAgent(words, strategy=Strategy.ENTROPY)
guess = agent.suggest()
agent.update(guess, feedback_pattern)

# Full offline episode
guesses = agent.solve("abril")
```

### Episode loop

```
env.reset(secret)
belief.reset()
while not done:
    action ← agent.suggest()          # policy π(b)
    obs, reward, done ← env.step(action)
    belief.update(action, pattern)    # filter hypothesis space
```

---

## How to make it better

1. **Word-frequency priors** — weight secrets by corpus frequency (SUBTLEX-ESP).
2. **Separate solution / guess sets** — common words for secrets, full dictionary for guesses.
3. **Hard mode** — constrain actions to reuse yellow/green letters.
4. **Performance** — cache `pattern()`, precompute opening guess, Numba for entropy.
5. **Benchmark suite** — simulate all secrets; report mean / median / p95 guesses.
6. **Neural policy** — train a network to imitate `WordleAgent.suggest()` as a fast heuristic.

---

## Project layout

```
Wordle/
├── lemario-general-del-espanol.txt
├── diagram.d2
├── pyproject.toml
├── Makefile
├── README.md
├── src/palabra_solver/
│   ├── data.py        # WordleWordsHandler
│   ├── env.py         # WordleEnv
│   ├── belief.py      # BeliefState
│   ├── agent.py       # WordleAgent
│   └── cli.py         # palabra command
└── tests/
    ├── test_words.py
    └── fixtures/
```

## License

Dictionary data: check the terms of the [lemario general del español](https://www.dle.rae.es/) source you used. Solver code: use as you see fit.
