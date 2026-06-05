"""Wordle model: inference over belief state to score and rank guesses."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence

from solver.data import PatternTable
from solver.env import WordleEnv


class WordleModel:
    """Maps belief (candidate secrets) to action values and best guesses."""

    def __init__(self, *, pattern_table: PatternTable | None = None) -> None:
        self.pattern_table = pattern_table

    def _pattern(self, secret: str, guess: str) -> int:
        if self.pattern_table is not None:
            return self.pattern_table.pattern(secret, guess)
        return WordleEnv.pattern(secret, guess)

    def partition(self, candidates: Sequence[str], guess: str) -> dict[int, list[str]]:
        """Group possible secrets by the feedback pattern they would produce."""
        buckets: dict[int, list[str]] = defaultdict(list)
        for candidate in candidates:
            buckets[self._pattern(candidate, guess)].append(candidate)
        return buckets

    def expected_entropy(self, guess: str, candidates: Sequence[str]) -> float:
        """Compute expected information H(g) in bits."""
        if not candidates:
            return 0.0

        total = len(candidates)
        entropy = 0.0
        for bucket in self.partition(candidates, guess).values():
            probability = len(bucket) / total
            entropy -= probability * math.log2(probability)
        return entropy

    def score_guess(self, guess: str, candidates: Sequence[str]) -> float:
        """Score a guess by expected information in bits."""
        return self.expected_entropy(guess, candidates)

    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
    ) -> str:
        """Pick the guess that maximizes expected entropy."""
        if not candidates:
            raise ValueError("candidates must not be empty")

        if len(candidates) == 1:
            return candidates[0]

        pool = guesses if guesses is not None else candidates
        best_word = pool[0]
        best_score = float("-inf")

        for guess in pool:
            score = self.score_guess(guess, candidates)
            if score > best_score or (score == best_score and guess < best_word):
                best_score = score
                best_word = guess

        return best_word
