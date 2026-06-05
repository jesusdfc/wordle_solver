"""Wordle agent: policy over belief state."""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence
from enum import Enum

from palabra_solver.belief import BeliefState
from palabra_solver.env import WordleEnv


class Strategy(Enum):
    ENTROPY = "entropy"
    MINIMAX = "minimax"


class WordleAgent:
    """Policy that maps belief state to optimal guesses."""

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
        initial = solution_words if solution_words is not None else all_words
        self.belief = BeliefState(initial)

    @property
    def candidates(self) -> tuple[str, ...]:
        return self.belief.candidates

    def reset(self) -> None:
        self.belief.reset()

    def suggest(self) -> str:
        """Choose the next guess from the current belief."""
        return self.best_guess(self.belief.candidates, self.all_words, strategy=self.strategy)

    def update(self, guess: str, feedback_pattern: int) -> None:
        """Incorporate a new observation into belief."""
        self.belief.update(guess, feedback_pattern)

    def act(self, env: WordleEnv) -> str:
        """Select an action and apply it to the environment."""
        guess = self.suggest()
        _, _, _, info = env.step(guess)
        self.update(guess, info["pattern"])
        return guess

    def solve(self, secret: str, *, max_guesses: int = 6) -> list[str]:
        """Run a full episode against a known secret (offline benchmark)."""
        if secret not in self.belief.candidates:
            raise ValueError(f"{secret!r} is not in the candidate word list")

        env = WordleEnv(self.all_words, max_guesses=max_guesses)
        env.reset(secret=secret)
        self.reset()

        played: list[str] = []
        for _ in range(max_guesses):
            if played and played[-1] == secret:
                break

            guess = self.belief.candidates[0] if self.belief.is_solved() else self.suggest()
            _, _, done, info = env.step(guess)
            self.update(guess, info["pattern"])
            played.append(guess)
            if done:
                break

        return played

    @staticmethod
    def partition(candidates: Sequence[str], guess: str) -> dict[int, list[str]]:
        """Group possible secrets by the feedback pattern they would produce."""
        buckets: dict[int, list[str]] = defaultdict(list)
        for candidate in candidates:
            buckets[WordleEnv.pattern(candidate, guess)].append(candidate)
        return buckets

    @staticmethod
    def expected_entropy(guess: str, candidates: Sequence[str]) -> float:
        """Compute expected information H(g) in bits."""
        if not candidates:
            return 0.0

        total = len(candidates)
        entropy = 0.0
        for bucket in WordleAgent.partition(candidates, guess).values():
            probability = len(bucket) / total
            entropy -= probability * math.log2(probability)
        return entropy

    @staticmethod
    def minimax_worst_case(guess: str, candidates: Sequence[str]) -> int:
        """Return the size of the largest remaining bucket after playing `guess`."""
        if not candidates:
            return 0
        return max(len(bucket) for bucket in WordleAgent.partition(candidates, guess).values())

    @staticmethod
    def score_guess(guess: str, candidates: Sequence[str], strategy: Strategy) -> float:
        if strategy is Strategy.ENTROPY:
            return WordleAgent.expected_entropy(guess, candidates)
        return -float(WordleAgent.minimax_worst_case(guess, candidates))

    @staticmethod
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
            score = WordleAgent.score_guess(guess, candidates, strategy)
            if score > best_score or (score == best_score and guess < best_word):
                best_score = score
                best_word = guess

        return best_word
