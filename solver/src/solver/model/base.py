"""Shared scoring utilities for Wordle guess models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Sequence

from solver.data import PatternTable
from solver.env import WordleEnv


class BaseModel(ABC):
    """Common interface for belief-scoring Wordle models."""

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

    @staticmethod
    def _candidate_key(candidates: Sequence[str]) -> tuple[str, ...]:
        return tuple(sorted(candidates))

    @abstractmethod
    def best_guess(
        self,
        candidates: Sequence[str],
        guesses: Sequence[str] | None = None,
        *,
        history: Sequence[str] | None = None,
    ) -> str:
        """Return the optimal next guess for the current belief."""
