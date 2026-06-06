"""Benchmark result types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GameResult:
    secret: str
    guesses: int
    solved: bool


@dataclass
class StrategyReport:
    strategy_id: str
    label: str
    games: list[GameResult]
    first_word: str = ""
    elapsed_seconds: float = 0.0
    belief_threshold: int | None = None
