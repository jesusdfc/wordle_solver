"""Wordle model: inference over belief state to score and rank guesses."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from enum import Enum

from solver.data import PatternTable
from solver.env import WordleEnv


class Strategy(Enum):
    ENTROPY = "entropy"
    MINIMAX = "minimax"


class WordleModel:
    """Maps belief (candidate secrets) to action values and best guesses."""

    def __init__(
        self,
        *,
        strategy: Strategy = Strategy.ENTROPY,
        pattern_table: PatternTable | None = None,
    ) -> None:
        self.strategy = strategy
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

    def minimax_worst_case(self, guess: str, candidates: Sequence[str]) -> float:
        """Return the size of the largest remaining bucket after playing `guess`."""
        if not candidates:
            return 0.0
        return float(max(len(bucket) for bucket in self.partition(candidates, guess).values()))

    def score_guess(self, guess: str, candidates: Sequence[str]) -> float:
        """Score a guess under the configured strategy."""
        if self.strategy is Strategy.ENTROPY:
            return self.expected_entropy(guess, candidates)
        return -self.minimax_worst_case(guess, candidates)

    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
    ) -> str:
        """Pick the guess that maximizes information under the configured strategy."""
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
