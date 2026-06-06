"""Threshold Bellman model: exact DP when belief is small, entropy otherwise."""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Sequence
from pathlib import Path

from solver.data.cache.bellman import ValueFunctionPersistor
from solver.model.base import BaseModel
from solver.model.entropy import EntropyModel

DEFAULT_BELIEF_THRESHOLD = 20


class ThresholdBellmanModel(BaseModel):
    """Use greedy entropy on large beliefs; exact Bellman DP when |B| < threshold."""

    def __init__(
        self,
        all_words: Sequence[str],
        *,
        pattern_table=None,
        length: int = 5,
        dictionary_path: Path | str | None = None,
        data_dir: Path | str | None = None,
        persist: bool = True,
        show_progress: bool = True,
        threshold: int = DEFAULT_BELIEF_THRESHOLD,
        cache_tag: str = "threshold_bellman",
    ) -> None:
        super().__init__(pattern_table=pattern_table)
        if not all_words:
            raise ValueError("all_words must not be empty")
        if threshold < 2:
            raise ValueError("threshold must be at least 2")

        self.all_words = tuple(all_words)
        self.length = length
        self.threshold = threshold
        self._entropy = EntropyModel(pattern_table=pattern_table)
        self._show_progress = show_progress
        self._progress_depth = 0
        self._persistor: ValueFunctionPersistor | None = None
        self._dirty = False

        if persist and dictionary_path is not None:
            self._persistor = ValueFunctionPersistor(
                dictionary_path,
                length=length,
                data_dir=data_dir,
                cache_tag=cache_tag,
            )
            self._value_cache = self._persistor.load(self.all_words)
        else:
            self._value_cache = {}

    def clear_cache(self) -> None:
        """Drop memoized value-function entries (memory only)."""
        self._value_cache.clear()
        self._dirty = False

    def flush_cache(self) -> None:
        """Persist the in-memory value function to disk."""
        if self._persistor is None or not self._dirty:
            return
        self._persistor.save(self.all_words, self._value_cache)
        self._dirty = False

    @property
    def cached_beliefs(self) -> int:
        """Number of beliefs currently stored in the value-function cache."""
        return len(self._value_cache)

    def _uses_bellman(self, candidates: Sequence[str]) -> bool:
        return len(candidates) < self.threshold

    def value(self, candidates: Sequence[str]) -> float:
        """Expected guesses to finish from belief *candidates* under optimal play."""
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
            self.all_words,
            desc=f"bellman_{self.length}_value_function |B|={len(key)}",
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
        """Bottom-up precompute V(B) for small beliefs reachable from *candidates*."""
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
                desc=f"bellman_{self.length}_discover_beliefs",
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

                for guess in self.all_words:
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
                desc=f"bellman_{self.length}_warm_cache beliefs={len(ordered)}",
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
                self.all_words,
                desc=f"bellman_{self.length}_value_function |B|={len(belief)}",
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

    def _partition_keys(
        self,
        candidates: Sequence[str],
        guess: str,
    ) -> list[tuple[str, ...]]:
        if self.pattern_table is not None:
            return self.pattern_table.partition_groups(candidates, guess)

        return [
            self._candidate_key(bucket)
            for bucket in self.partition(candidates, guess).values()
        ]

    @staticmethod
    def _guess_order(candidates: Sequence[str], pool: Sequence[str]) -> tuple[str, ...]:
        """Belief words first, then remaining probe words from *pool*."""
        in_belief = set(candidates)
        return tuple(candidates) + tuple(word for word in pool if word not in in_belief)

    def _scan_guesses(
        self,
        candidates: Sequence[str],
        pool: Sequence[str],
        *,
        desc: str,
    ) -> tuple[str, float]:
        """Return the guess with minimum expected cost and that cost."""
        ordered = self._guess_order(candidates, pool)
        show_bar = self._show_progress and self._progress_depth == 0
        self._progress_depth += 1
        try:
            best_word = ordered[0]
            best_cost = float("inf")

            iterable: Sequence[str] = ordered
            bar = None
            if show_bar:
                from tqdm import tqdm

                bar = tqdm(ordered, desc=desc, unit=" guesses")
                iterable = bar

            for guess in iterable:
                cost = self.expected_cost(guess, candidates, upper_bound=best_cost)
                if cost < best_cost or (cost == best_cost and guess < best_word):
                    best_cost = cost
                    best_word = guess
                if bar is not None:
                    bar.set_postfix(cached=len(self._value_cache), refresh=False)

            if bar is not None:
                bar.close()
            return best_word, best_cost
        finally:
            self._progress_depth -= 1

    def expected_cost(
        self,
        guess: str,
        candidates: Sequence[str],
        *,
        upper_bound: float = float("inf"),
    ) -> float:
        """Expected total guesses if we play *guess* now and optimally thereafter."""
        key = self._candidate_key(candidates)
        total = len(candidates)
        cost = 0.0
        for substate in self._partition_keys(candidates, guess):
            if substate == key:
                return float("inf")
            probability = len(substate) / total
            if len(substate) >= self.threshold:
                remaining = 0.0 if len(substate) == 1 else math.ceil(math.log2(len(substate)))
                cost += probability * (1.0 + remaining)
            else:
                cost += probability * (1.0 + self.value(substate))
            if cost >= upper_bound:
                return float("inf")
        return cost

    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
        *,
        history: Sequence[str] | None = None,
    ) -> str:
        """Entropy on large beliefs; Bellman when |B| < threshold."""
        if not candidates:
            raise ValueError("candidates must not be empty")

        if len(candidates) == 1:
            return candidates[0]

        pool = guesses if guesses is not None else self.all_words
        if not self._uses_bellman(candidates):
            return self._entropy.best_guess(candidates, pool, history=history)

        best_word, _ = self._scan_guesses(
            candidates,
            pool,
            desc=f"bellman_{self.length}_best_guess |B|={len(candidates)}",
        )
        return best_word
