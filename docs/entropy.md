# Entropy strategy

Greedy **expected-information** policy for Spanish Wordle. At each turn the solver picks the guess whose feedback partition has maximum Shannon entropy under a **uniform prior** over remaining secrets.

## Problem setup

Wordle is a partially observable game:

- **Belief** \(\mathcal{B}\): dictionary words still consistent with all guesses so far.
- **Action**: a guess \(g\) from the full dictionary (including probe words).
- **Observation**: color pattern \(p = \mathrm{pattern}(s, g)\) for the hidden secret \(s\).
- **Prior**: uniform on \(\mathcal{B}\) — no frequency data assumed.

Implementation: `solver/src/solver/model/entropy.py` (`EntropyModel`). Set `first_word` to pin the opening guess (`fixed-entropy` strategy); leave it empty for greedy entropy every turn (`full-entropy`).

## Partition

For belief \(\mathcal{B}\) with \(N = |\mathcal{B}|\) and guess \(g\):

$$
\mathcal{B} = \bigsqcup_{p} B_p, \qquad B_p = \{\, s \in \mathcal{B} : \mathrm{pattern}(s, g) = p \,\}
$$

Let \(n_p = |B_p|\). Under a uniform prior:

$$
\mathbb{P}(p \mid g, \mathcal{B}) = \frac{n_p}{N}
$$

## Shannon entropy score

$$
H(g) = -\sum_{p} \frac{n_p}{N} \log_2 \frac{n_p}{N}
$$

This is what `EntropyModel.expected_entropy` computes.

**Interpretation:** \(H(g)\) is the expected number of bits gained from the next feedback. Equivalently:

$$
\mathbb{E}[\text{reduction}] = \sum_p \frac{n_p}{N}\left(\log_2 N - \log_2 n_p\right) = H(g)
$$

## Policy

$$
g^* = \arg\max_{g \in \mathcal{W}} H(g)
$$

Tie-break: lexicographically smallest word.

Maximizing \(H(g)\) pushes bin probabilities toward equal size. For \(k\) bins, entropy is largest when every \(n_p \approx N/k\).

| Property | Effect |
|----------|--------|
| **Maximum** \(H(g)\) | Balanced bins → steady expected shrinkage |
| **Minimum** \(H(g)\) | One dominant bin → usually learn little |
| **Units** | Bits; \(H(g) = \log_2 k\) when all bins equal |

### Example

\(N = 8\), bin sizes 3, 3, 2:

$$
H \approx 1.56\ \text{bits}
$$

Skewed bins 7, 1, 0:

$$
H \approx 0.54\ \text{bits}
$$

### Two-bin case

When only two patterns appear with counts \(n\) and \(N-n\):

$$
H(g) = -\frac{n}{N}\log_2\frac{n}{N} - \frac{N-n}{N}\log_2\frac{N-n}{N}
$$

Maximum at \(n = N/2\) (\(H = 1\) bit).

## What “optimal” means here

Entropy maximization is **myopically optimal** for expected information on the **next** guess. It is **not** guaranteed to minimize expected **total** guesses to win — that requires multi-step dynamic programming (see [bellman.md](bellman.md)).

Entropy also differs slightly from minimizing expected remaining word count \(\sum_p n_p^2 / N\), though the two align for perfect 50/50 splits.

## When to use

- Fast on large dictionaries (~5k words).
- Strong default when word frequencies are unknown.
- Good opening probes from the full dictionary, not only remaining candidates.

```bash
cd solver && uv run palabra suggest --strategy entropy --guess audio02201
```
