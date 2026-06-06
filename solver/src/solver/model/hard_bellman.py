"""Hard-mode threshold Bellman: probe only from remaining candidates."""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence

from solver.model.threshold_bellman import DEFAULT_BELIEF_THRESHOLD, ThresholdBellmanModel


class HardBellmanModel(ThresholdBellmanModel):
    """Greedy entropy on large beliefs; hard-mode Bellman when |B| < threshold.

    Hard mode restricts Bellman probes to the current candidate set instead of the
    full dictionary, which is much faster on small endgame beliefs.
    """

    def __init__(
        self,
        all_words: Sequence[str],
        *,
        pattern_table=None,
        length: int = 5,
        dictionary_path=None,
        data_dir=None,
        persist: bool = True,
        show_progress: bool = True,
        threshold: int = DEFAULT_BELIEF_THRESHOLD,
    ) -> None:
        super().__init__(
            all_words,
            pattern_table=pattern_table,
            length=length,
            dictionary_path=dictionary_path,
            data_dir=data_dir,
            persist=persist,
            show_progress=show_progress,
            threshold=threshold,
            cache_tag="hard_bellman",
        )

    @staticmethod
    def _hard_pool(candidates: Sequence[str]) -> tuple[str, ...]:
        return tuple(candidates)

    def value(self, candidates: Sequence[str]) -> float:
        """Expected guesses under hard-mode Bellman from belief *candidates*."""
        key = self._candidate_key(candidates)
        if not key:
            return 0.0
        if len(key) == 1:
            return 1.0
        if len(key) >= self.threshold:
            raise ValueError(
                f"value() requires |B| < {self.threshold}; got {len(key)} candidates"
            )

        cached = self._value_cache.get(key)
        if cached is not None:
            return cached

        _, best_cost = self._scan_guesses(
            key,
            self._hard_pool(key),
            desc=f"hard_bellman_{self.length}_value_function |B|={len(key)}",
        )
        self._value_cache[key] = best_cost
        self._dirty = True
        return best_cost

    def warm_cache(
        self,
        candidates: Sequence[str] | None = None,
        *,
        max_beliefs: int | None = None,
    ) -> int:
        """Bottom-up precompute V(B) for small hard-mode beliefs."""
        root = self._candidate_key(candidates or self.all_words)
        if not root:
            return 0
        if len(root) == 1:
            was_new = root not in self._value_cache
            if was_new:
                self._value_cache[root] = 1.0
                self._dirty = True
                self.flush_cache()
            return int(was_new)

        visited: set[tuple[str, ...]] = {root}
        queue: deque[tuple[str, ...]] = deque([root])

        discover_bar = None
        if self._show_progress:
            from tqdm import tqdm

            discover_bar = tqdm(
                desc=f"hard_bellman_{self.length}_discover_beliefs",
                unit=" beliefs",
            )

        try:
            while queue:
                if max_beliefs is not None and len(visited) >= max_beliefs:
                    break

                belief = queue.popleft()
                if discover_bar is not None:
                    discover_bar.update(1)
                    discover_bar.set_postfix(
                        discovered=len(visited),
                        queued=len(queue),
                        refresh=False,
                    )

                for guess in belief:
                    for substate in self._partition_keys(belief, guess):
                        if substate == belief or substate in visited:
                            continue
                        visited.add(substate)
                        queue.append(substate)
        finally:
            if discover_bar is not None:
                discover_bar.close()

        small_beliefs = [belief for belief in visited if len(belief) < self.threshold]
        ordered = sorted(small_beliefs, key=len)
        iterable: Sequence[tuple[str, ...]] = ordered
        bar = None
        if self._show_progress:
            from tqdm import tqdm

            bar = tqdm(
                ordered,
                desc=f"hard_bellman_{self.length}_warm_cache beliefs={len(ordered)}",
                unit=" beliefs",
            )
            iterable = bar

        solved = 0
        for belief in iterable:
            if len(belief) == 1:
                if belief not in self._value_cache:
                    self._value_cache[belief] = 1.0
                    self._dirty = True
                    solved += 1
                continue

            if belief in self._value_cache:
                continue

            _, best_cost = self._scan_guesses(
                belief,
                self._hard_pool(belief),
                desc=f"hard_bellman_{self.length}_value_function |B|={len(belief)}",
            )
            self._value_cache[belief] = best_cost
            self._dirty = True
            solved += 1
            if bar is not None:
                bar.set_postfix(cached=len(self._value_cache), refresh=False)

        if bar is not None:
            bar.close()

        self.flush_cache()
        return solved

    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
        *,
        history: Sequence[str] | None = None,
    ) -> str:
        """Entropy on large beliefs; hard-mode Bellman when |B| < threshold."""
        if not candidates:
            raise ValueError("candidates must not be empty")

        if len(candidates) == 1:
            return candidates[0]

        pool = guesses if guesses is not None else self.all_words
        if not self._uses_bellman(candidates):
            return self._entropy.best_guess(candidates, pool, history=history)

        best_word, _ = self._scan_guesses(
            candidates,
            self._hard_pool(candidates),
            desc=f"hard_bellman_{self.length}_best_guess |B|={len(candidates)}",
        )
        return best_word
