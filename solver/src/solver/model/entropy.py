"""Greedy entropy (expected information) Wordle model."""

from __future__ import annotations

import math
from collections.abc import Sequence

from solver.model.base import BaseModel


class EntropyModel(BaseModel):
    """Pick the guess that maximizes expected Shannon entropy of the pattern split."""

    def __init__(
        self,
        *,
        pattern_table=None,
        first_word: str = "",
        all_words: Sequence[str] | None = None,
    ) -> None:
        super().__init__(pattern_table=pattern_table)
        self.first_word = first_word.strip().lower()
        self.all_words = tuple(all_words) if all_words is not None else ()
        if self.first_word and self.all_words and self.first_word not in self.all_words:
            raise ValueError(f"first_word {self.first_word!r} is not in the dictionary")

    def expected_entropy(self, guess: str, candidates: Sequence[str]) -> float:
        """Compute expected information H(g) in bits."""
        if not candidates:
            return 0.0

        if self.pattern_table is not None:
            try:
                counts = self.pattern_table.bucket_sizes(candidates, guess)
            except KeyError:
                pass
            else:
                import numpy as np

                total = len(candidates)
                probabilities = counts / total
                return float(-np.sum(probabilities * np.log2(probabilities)))

        total = len(candidates)
        entropy = 0.0
        for bucket in self.partition(candidates, guess).values():
            probability = len(bucket) / total
            entropy -= probability * math.log2(probability)
        return entropy

    def score_guess(self, guess: str, candidates: Sequence[str]) -> float:
        """Score a guess by expected information in bits."""
        return self.expected_entropy(guess, candidates)

    def _best_guess_from_scores(
        self,
        pool: Sequence[str],
        scores: Sequence[float],
    ) -> str:
        best_word = pool[0]
        best_score = float("-inf")
        for word, score in zip(pool, scores, strict=True):
            if score > best_score or (score == best_score and word < best_word):
                best_score = score
                best_word = word
        return best_word

    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
        *,
        history: Sequence[str] | None = None,
    ) -> str:
        """Pick the guess that maximizes expected entropy (or *first_word* on turn 1)."""
        if not candidates:
            raise ValueError("candidates must not be empty")

        if len(candidates) == 1:
            return candidates[0]

        if not history and self.first_word:
            return self.first_word

        pool = guesses if guesses is not None else candidates

        if self.pattern_table is not None:
            try:
                scores = self.pattern_table.entropy_scores(candidates, pool)
            except KeyError:
                pass
            else:
                return self._best_guess_from_scores(pool, scores)

        return self._best_guess_from_scores(
            pool,
            [self.score_guess(guess, candidates) for guess in pool],
        )
