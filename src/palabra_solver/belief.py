"""Belief state over hidden secrets in a POMDP Wordle game."""

from __future__ import annotations

from collections.abc import Sequence

from palabra_solver.env import WordleEnv


class BeliefState:
    """Posterior over possible secrets given observation history."""

    def __init__(self, candidates: Sequence[str]) -> None:
        if not candidates:
            raise ValueError("candidates must not be empty")
        self._initial = tuple(candidates)
        self._candidates = self._initial

    @property
    def candidates(self) -> tuple[str, ...]:
        return self._candidates

    @property
    def size(self) -> int:
        return len(self._candidates)

    def reset(self, candidates: Sequence[str] | None = None) -> None:
        """Restore belief to the initial (or given) candidate set."""
        self._candidates = tuple(candidates if candidates is not None else self._initial)

    def update(self, guess: str, feedback_pattern: int) -> None:
        """Bayesian filter: keep secrets consistent with the observed pattern."""
        self._candidates = tuple(
            candidate
            for candidate in self._candidates
            if WordleEnv.pattern(candidate, guess) == feedback_pattern
        )

    def is_solved(self) -> bool:
        return len(self._candidates) == 1

    def is_empty(self) -> bool:
        return len(self._candidates) == 0
