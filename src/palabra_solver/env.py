"""Wordle environment: hidden state, dynamics, and observations."""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class WordleObservation:
    """What the agent sees after each turn (no access to the secret)."""

    guesses: tuple[str, ...]
    patterns: tuple[int, ...]
    turn: int


class WordleEnv:
    """Stateful Wordle simulator (POMDP environment)."""

    GRAY = 0
    YELLOW = 1
    GREEN = 2

    _PATTERN_SYMBOLS = ("⬛", "🟨", "🟩")
    _ASCII_SYMBOLS = (".", "y", "g")

    def __init__(
        self,
        words: Sequence[str],
        *,
        max_guesses: int = 6,
        word_length: int | None = None,
    ) -> None:
        if not words:
            raise ValueError("words must not be empty")

        self.words = tuple(words)
        self.max_guesses = max_guesses
        self.word_length = word_length or len(self.words[0])
        self._secret: str | None = None
        self._guesses: list[str] = []
        self._patterns: list[int] = []

    @property
    def secret(self) -> str | None:
        return self._secret

    @property
    def observation(self) -> WordleObservation:
        return WordleObservation(
            guesses=tuple(self._guesses),
            patterns=tuple(self._patterns),
            turn=len(self._guesses),
        )

    @property
    def done(self) -> bool:
        if not self._guesses:
            return False
        return self._guesses[-1] == self._secret or len(self._guesses) >= self.max_guesses

    def reset(self, *, secret: str | None = None) -> WordleObservation:
        """Start a new episode. Sample a secret if none is provided."""
        if secret is not None:
            if secret not in self.words:
                raise ValueError(f"{secret!r} is not in the word list")
            self._secret = secret
        else:
            self._secret = random.choice(self.words)

        self._guesses = []
        self._patterns = []
        return self.observation

    def step(self, guess: str) -> tuple[WordleObservation, float, bool, dict]:
        """Apply an action and return (observation, reward, done, info)."""
        if self._secret is None:
            raise RuntimeError("call reset() before step()")
        if self.done:
            raise RuntimeError("episode is already finished")

        guess = guess.lower()
        if guess not in self.words:
            raise ValueError(f"{guess!r} is not a valid word")

        pattern = self.pattern(self._secret, guess)
        self._guesses.append(guess)
        self._patterns.append(pattern)

        won = guess == self._secret
        finished = won or len(self._guesses) >= self.max_guesses
        reward = 1.0 if won else (-1.0 if finished else 0.0)

        info = {"pattern": pattern, "won": won}
        return self.observation, reward, finished, info

    @staticmethod
    def pattern(secret: str, guess: str) -> int:
        """Observation function: feedback for `guess` against `secret` as base-3 int."""
        if len(secret) != len(guess):
            raise ValueError("secret and guess must have the same length")

        length = len(secret)
        codes = [WordleEnv.GRAY] * length
        remaining: dict[str, int] = {}

        for letter in secret:
            remaining[letter] = remaining.get(letter, 0) + 1

        for index, (secret_letter, guess_letter) in enumerate(zip(secret, guess, strict=True)):
            if guess_letter == secret_letter:
                codes[index] = WordleEnv.GREEN
                remaining[guess_letter] -= 1

        for index, guess_letter in enumerate(guess):
            if codes[index] == WordleEnv.GREEN:
                continue
            if remaining.get(guess_letter, 0) > 0:
                codes[index] = WordleEnv.YELLOW
                remaining[guess_letter] -= 1

        value = 0
        for index, code in enumerate(codes):
            value += code * (3**index)
        return value

    @staticmethod
    def pattern_to_str(value: int, *, length: int = 5, use_emoji: bool = True) -> str:
        """Render a pattern integer as emoji tiles or ASCII letters."""
        symbols = WordleEnv._PATTERN_SYMBOLS if use_emoji else WordleEnv._ASCII_SYMBOLS

        rendered: list[str] = []
        for index in range(length):
            code = (value // (3**index)) % 3
            rendered.append(symbols[code])
        return "".join(rendered)
