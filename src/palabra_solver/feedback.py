"""Wordle feedback patterns encoded as base-3 integers."""

from __future__ import annotations

GRAY = 0
YELLOW = 1
GREEN = 2

_PATTERN_SYMBOLS = ("⬛", "🟨", "🟩")


def pattern(secret: str, guess: str) -> int:
    """Return feedback for `guess` against `secret` as an integer in [0, 3**len)."""
    if len(secret) != len(guess):
        raise ValueError("secret and guess must have the same length")

    length = len(secret)
    codes = [GRAY] * length
    remaining: dict[str, int] = {}

    for letter in secret:
        remaining[letter] = remaining.get(letter, 0) + 1

    for index, (secret_letter, guess_letter) in enumerate(zip(secret, guess, strict=True)):
        if guess_letter == secret_letter:
            codes[index] = GREEN
            remaining[guess_letter] -= 1

    for index, guess_letter in enumerate(guess):
        if codes[index] == GREEN:
            continue
        if remaining.get(guess_letter, 0) > 0:
            codes[index] = YELLOW
            remaining[guess_letter] -= 1

    value = 0
    for index, code in enumerate(codes):
        value += code * (3**index)
    return value


def pattern_to_str(value: int, *, length: int = 5, use_emoji: bool = True) -> str:
    """Render a pattern integer as emoji tiles or ASCII letters for terminals."""
    if use_emoji:
        symbols = _PATTERN_SYMBOLS
    else:
        symbols = (".", "y", "g")

    rendered: list[str] = []
    for index in range(length):
        code = (value // (3**index)) % 3
        rendered.append(symbols[code])
    return "".join(rendered)
