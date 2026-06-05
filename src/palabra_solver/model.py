"""Entropy and minimax solvers for Wordle."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from enum import Enum

from palabra_solver.feedback import pattern


class Strategy(Enum):
    ENTROPY = "entropy"
    MINIMAX = "minimax"


def partition(candidates: Sequence[str], guess: str) -> dict[int, list[str]]:
    """Group possible secrets by the feedback pattern they would produce."""
    buckets: dict[int, list[str]] = defaultdict(list)
    for candidate in candidates:
        buckets[pattern(candidate, guess)].append(candidate)
    return buckets


def expected_entropy(guess: str, candidates: Sequence[str]) -> float:
    """Compute expected information H(g) in bits."""
    if not candidates:
        return 0.0

    total = len(candidates)
    entropy = 0.0
    for bucket in partition(candidates, guess).values():
        probability = len(bucket) / total
        entropy -= probability * math.log2(probability)
    return entropy


def minimax_worst_case(guess: str, candidates: Sequence[str]) -> int:
    """Return the size of the largest remaining bucket after playing `guess`."""
    if not candidates:
        return 0
    return max(len(bucket) for bucket in partition(candidates, guess).values())


def score_guess(guess: str, candidates: Sequence[str], strategy: Strategy) -> float:
    if strategy is Strategy.ENTROPY:
        return expected_entropy(guess, candidates)
    return -float(minimax_worst_case(guess, candidates))


def best_guess(
    candidates: Sequence[str],
    guesses: Sequence[str] | None = None,
    *,
    strategy: Strategy = Strategy.ENTROPY,
) -> str:
    """Pick the guess that maximizes information under the chosen strategy."""
    if not candidates:
        raise ValueError("candidates must not be empty")

    if len(candidates) == 1:
        return candidates[0]

    pool = guesses if guesses is not None else candidates
    best_word = pool[0]
    best_score = float("-inf")

    for guess in pool:
        score = score_guess(guess, candidates, strategy)
        if score > best_score or (score == best_score and guess < best_word):
            best_score = score
            best_word = guess

    return best_word


class Solver:
    """Maintain the hypothesis space and suggest optimal guesses."""

    def __init__(
        self,
        all_words: Sequence[str],
        solution_words: Sequence[str] | None = None,
        *,
        strategy: Strategy = Strategy.ENTROPY,
    ) -> None:
        if not all_words:
            raise ValueError("all_words must not be empty")

        self.all_words = tuple(all_words)
        self.strategy = strategy
        self._initial_candidates = tuple(
            solution_words if solution_words is not None else all_words
        )
        self._candidates = self._initial_candidates
        self._guesses: list[str] = []

    def reset(self) -> None:
        self._candidates = self._initial_candidates
        self._guesses = []

    @property
    def candidates(self) -> tuple[str, ...]:
        return self._candidates

    @property
    def guesses(self) -> tuple[str, ...]:
        return tuple(self._guesses)

    def suggest(self) -> str:
        return best_guess(self._candidates, self.all_words, strategy=self.strategy)

    def update(self, guess: str, feedback_pattern: int) -> None:
        """Filter candidates using the observed feedback pattern."""
        self._guesses.append(guess)
        self._candidates = tuple(
            candidate
            for candidate in self._candidates
            if pattern(candidate, guess) == feedback_pattern
        )

    def is_solved(self) -> bool:
        return len(self._candidates) == 1

    def solve(self, secret: str, *, max_guesses: int = 6) -> list[str]:
        """Simulate a full game offline for benchmarking."""
        if secret not in self._initial_candidates:
            raise ValueError(f"{secret!r} is not in the candidate word list")

        self.reset()
        played: list[str] = []
        for _ in range(max_guesses):
            if played and played[-1] == secret:
                break

            guess = self._candidates[0] if len(self._candidates) == 1 else self.suggest()
            played.append(guess)
            self.update(guess, pattern(secret, guess))
            if guess == secret:
                break

        return played
