# Palabra Solver

Optimal entropy-based solver for **La Palabra del Día** (Spanish Wordle). Given past guesses and feedback, it picks the next guess that **maximizes expected information** about the hidden word.

## How the entropy solver works

Wordle is a **partially observable** guessing game: the secret is hidden, but each guess returns a color pattern (⬛ gray, 🟨 yellow, 🟩 green). The solver treats that as a filtering problem:

1. **Belief** — maintain the set of dictionary words still consistent with every guess so far.
2. **Partition** — for a candidate guess, group those words by the pattern each would produce.
3. **Score** — pick the guess whose pattern bins are as **evenly sized** as possible.
4. **Update** — after real feedback arrives, keep only the bin that matches and repeat.

The implementation lives in `solver/src/solver/belief.py` (belief update) and `solver/src/solver/model.py` (partition + entropy scoring). The agent evaluates guesses from the **full dictionary**, not only remaining candidates, so it can suggest strong “probe” words early on.

### Pattern bins (pathways)

Each guess splits the current belief into **bins** — one per possible feedback pattern. You only observe **one** bin after the guess; the others are paths you did not take.

```mermaid
flowchart TB
    subgraph before ["Belief before guess · N = 12 candidates"]
        direction LR
        c["abril · abono · abajo · abano · …"]
    end

    g["Guess: AUDIO"]

    subgraph bins ["Pattern bins (pathways)"]
        direction TB
        b1["⬛⬛⬛⬛⬛  ·  5 words"]
        b2["⬛🟨⬛⬛⬛  ·  4 words"]
        b3["⬛⬛🟩⬛⬛  ·  3 words"]
    end

    subgraph after ["Belief after feedback"]
        direction LR
        kept["Keep one bin only → 3–5 candidates left"]
    end

    before --> g --> bins
    bins -->|"you see one pattern"| after
```

**Stable vs. skewed splits.** A good entropy guess makes the bins similar in size — no matter which pattern appears, you eliminate roughly the same fraction of the belief. A bad guess puts almost every secret in one giant bin: most of the time you learn almost nothing, and only a rare pattern would narrow the search sharply.

```mermaid
flowchart LR
    subgraph good ["High entropy · balanced bins"]
        direction TB
        g1["Bin A · 33%"]
        g2["Bin B · 33%"]
        g3["Bin C · 34%"]
    end

    subgraph bad ["Low entropy · one dominant bin"]
        direction TB
        b1["Bin A · 92%"]
        b2["Bin B · 5%"]
        b3["Bin C · 3%"]
    end
```

That balance is what people mean by a **stable** strategy: outcomes are spread evenly, so expected progress per guess is predictable instead of relying on a lucky pattern.

### Mathematics

#### Belief state

After observations $(g_1, p_1), \ldots, (g_t, p_t)$, the belief is the set of secrets still compatible with the rules of Wordle feedback:

$$
\mathcal{B}_t = \{\, s \in \mathcal{W} \mid \forall i \le t:\ \mathrm{pattern}(s, g_i) = p_i \,\}
$$

We use a **uniform prior** over $\mathcal{B}_t$: every remaining word is equally likely to be the secret.

#### Partition induced by a guess

Fix a guess $g$ and current belief $\mathcal{B}$ with $N = |\mathcal{B}|$. Each secret $s \in \mathcal{B}$ produces an integer pattern $p = \mathrm{pattern}(s, g)$ (gray / yellow / green encoded as a single code). This defines a partition into bins:

$$
\mathcal{B} = \bigsqcup_{p \in \mathcal{P}(g)} B_p, \qquad B_p = \{\, s \in \mathcal{B} : \mathrm{pattern}(s, g) = p \,\}
$$

Let $n_p = |B_p|$. If the secret is uniform on $\mathcal{B}$, the probability of seeing pattern $p$ after guessing $g$ is:

$$
\mathbb{P}(p \mid g, \mathcal{B}) = \frac{n_p}{N}
$$

#### Shannon entropy of the split

The **expected entropy** (expected information, in **bits**) of guess $g$ is the Shannon entropy of that distribution:

$$
H(g) = -\sum_{p} \frac{n_p}{N} \log_2 \frac{n_p}{N}
$$

This is exactly what `WordleModel.expected_entropy` computes: group candidates into bins, then apply $-\sum p \log_2 p$.

**Interpretation:** $H(g)$ is the average number of bits of information you expect to gain from the feedback. Equivalently, if the secret were chosen uniformly from $\mathcal{B}$, observing the pattern reduces uncertainty from $\log_2 N$ bits to $\log_2 n_p$ bits; averaging over $p$ gives:

$$
\mathbb{E}[\text{reduction}] = \sum_p \frac{n_p}{N}\left(\log_2 N - \log_2 n_p\right) = H(g)
$$

#### Why maximize entropy?

The solver chooses:

$$
g^* = \arg\max_{g \in \mathcal{W}} H(g)
$$

(tie-break: lexicographically smallest word).

Maximizing $H(g)$ pushes the bin probabilities $n_p/N$ toward **equal size**. For a fixed number of bins $k$, entropy is largest when every bin has $n_p \approx N/k$ — the most **evenly distributed** split.

| Property | Effect |
|----------|--------|
| **Maximum** $H(g)$ | Bins are balanced → typical feedback shrinks the belief by a steady factor |
| **Minimum** $H(g)$ | One bin dominates → you usually stay in a huge candidate set |
| **Units** | Bits; $H(g) = \log_2 k$ when all $k$ bins are equal |

**Example.** $N = 8$ candidates, three bins of sizes 3, 3, 2:

$$
H = -\tfrac{3}{8}\log_2\tfrac{3}{8} - \tfrac{3}{8}\log_2\tfrac{3}{8} - \tfrac{2}{8}\log_2\tfrac{2}{8} \approx 1.56\ \text{bits}
$$

If instead bins were 7, 1, 0 (one heavy pathway):

$$
H \approx 0.54\ \text{bits}
$$

Same game, same dictionary — the balanced guess is preferred because it **maximizes expected information** regardless of which color pattern the game returns.

#### Closed form for two bins

When a guess splits the belief into exactly two patterns with counts $n$ and $N - n$:

$$
H(g) = -\frac{n}{N}\log_2\frac{n}{N} - \frac{N-n}{N}\log_2\frac{N-n}{N}
$$

This is maximized at $n = N/2$ (a perfect 50/50 split, $H = 1$ bit). Wordle partitions usually have more than two bins, but the same principle holds: **spread the probability mass evenly across pathways**.

---

## Solver package

Python package: `wordle-solver` in `solver/`.

```bash
# Install and run tests
make test

# Lint / format
make checks
```

**CLI:**

```bash
cd solver && uv sync
uv run palabra suggest --guess audio02201   # next guess from feedback string
uv run palabra solve abril                  # auto-play a secret word
```

Feedback encoding in `--guess`: `0` = gray, `1` = yellow, `2` = green (per letter, left to right).

### First run / caches

On first use the solver builds cached files (gitignored, regenerated automatically):

- `words_5.pickle` — normalized word list
- `word_5_dict.pickle` — pattern lookup matrix (~25 MB, ~45 s to build once)

By default these live under `data/`. Override with the `WORDLE_CACHE_DIR` environment variable if needed.

## Dictionary

Word list: [`lemario-general-del-espanol.txt`](https://github.com/olea/lemarios/blob/master/lemario-general-del-espanol.txt) from [olea/lemarios](https://github.com/olea/lemarios) (public domain).

Bundled copy: `data/lemario-general-del-espanol.txt`.

## License

MIT — see [LICENSE](LICENSE).

Word list data from [olea/lemarios](https://github.com/olea/lemarios) (public domain), not covered by MIT.
