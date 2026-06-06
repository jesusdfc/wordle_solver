# Threshold Bellman strategy

**Hybrid policy**: greedy entropy while the belief is large, then **exact dynamic programming** when \(|\mathcal{B}| < \text{threshold}\) (default **20**). This keeps play fast on early turns while still finishing optimally once the candidate set is small.

Implementation: `solver/src/solver/model/threshold_bellman.py` (`ThresholdBellmanModel`).

Hybrid strategies (`entropy-threshold-bellman`, `entropy-hard-bellman`) use a greedy **entropy opening guess** on turn 1, then delegate to Bellman from turn 2 onward. `fixed-entropy` uses a user-chosen first word via `EntropyModel.first_word`, then entropy for all later guesses.

## Policy rule

| Belief size | Policy |
|-------------|--------|
| \(|\mathcal{B}| \ge \text{threshold}\) | Greedy entropy over full dictionary |
| \(|\mathcal{B}| < \text{threshold}\) | Exact Bellman DP |

Turn 1 of hybrid strategies uses a greedy entropy opening guess; `fixed-entropy` uses `EntropyModel.first_word` instead. Bellman never runs on turn 1.

## MDP formulation (small beliefs)

| Component | Wordle |
|-----------|--------|
| **State** | Belief \(\mathcal{B}\) (remaining candidate secrets) |
| **Action** | Guess \(g \in \mathcal{W}\) |
| **Transition** | Deterministic pattern \(p\) given secret \(s \in \mathcal{B}\) |
| **Cost** | 1 per guess (minimize total guesses) |

## Value function

\(V(\mathcal{B})\) is defined only for \(|\mathcal{B}| < \text{threshold}\).

**Base case:** if \(|\mathcal{B}| = 1\), one guess wins → \(V(\mathcal{B}) = 1\).

**Bellman equation:**

$$
V(\mathcal{B}) = \min_{g \in \mathcal{W}} \left[ 1 + \sum_p \frac{n_p}{N}\, \text{cost}(\mathcal{B}_p) \right]
$$

where \(\text{cost}(\mathcal{B}_p) = V(\mathcal{B}_p)\) if \(|\mathcal{B}_p| < \text{threshold}\), otherwise a cheap entropy-style estimate \(\lceil \log_2 |\mathcal{B}_p| \rceil\).

`ThresholdBellmanModel.best_guess` switches between entropy and Bellman based on \(|\mathcal{B}|\). `ThresholdBellmanModel.value` memoizes \(V(\mathcal{B})\) over `tuple(sorted(candidates))` for small beliefs only.

## Relation to entropy

| | Entropy | Threshold Bellman |
|---|---------|-------------------|
| **Objective** | Max bits gained *now* | Min expected guesses when \(|\mathcal{B}|\) is small |
| **Horizon** | 1 step (greedy) | Full game (via \(V\)) on small beliefs |
| **Computation** | Cheap | Expensive only when \(|\mathcal{B}| < 20\) |
| **Optimality** | Optimal for next-step information | Optimal for expected guess count on small beliefs |

## Complexity

Bellman runs only on beliefs with fewer than 20 candidates, so each step scans ~5k guesses but recurses into tiny sub-beliefs. The opening turn uses entropy (or a fixed word), not Bellman.

Practical tips:

- Reuse one `ThresholdBellmanModel` across many games so the in-memory cache grows.
- Call `flush_cache()` (or use the CLI/API agent) to persist memoized values to `data/cache/threshold_bellman_{length}_value_function.pickle` (hard mode: `hard_bellman_{length}_value_function.pickle`).
- The pickle stores \(V(\mathcal{B})\) for small beliefs already solved; it grows incrementally.

```bash
cd solver && uv run palabra explore --strategy entropy-threshold-bellman abril
cd solver && uv run palabra warm-bellman-cache
```

See also: [entropy.md](entropy.md) for the greedy baseline.
