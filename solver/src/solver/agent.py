"""Wordle agent: executes policy against the environment."""

from __future__ import annotations

from collections.abc import Sequence

from solver.belief import BeliefState
from solver.data import PatternTable
from solver.env import WordleEnv
from solver.model import Strategy, WordleModel


class WordleAgent:
    """Stateful actor that maintains belief and acts via a model."""

    def __init__(
        self,
        all_words: Sequence[str],
        solution_words: Sequence[str] | None = None,
        *,
        model: WordleModel | None = None,
        strategy: Strategy = Strategy.ENTROPY,
        pattern_table: PatternTable | None = None,
    ) -> None:
        if not all_words:
            raise ValueError("all_words must not be empty")

        self.all_words = tuple(all_words)
        self.pattern_table = pattern_table
        self.model = model or WordleModel(strategy=strategy, pattern_table=pattern_table)
        initial = solution_words if solution_words is not None else all_words
        self.belief = BeliefState(initial, pattern_table=pattern_table)

    @property
    def candidates(self) -> tuple[str, ...]:
        return self.belief.candidates

    def reset(self) -> None:
        self.belief.reset()

    def suggest(self) -> str:
        """Choose the next guess from the current belief."""
        return self.model.best_guess(self.belief.candidates, self.all_words)

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
