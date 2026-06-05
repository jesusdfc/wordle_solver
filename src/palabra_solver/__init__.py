"""Optimal solver for La Palabra del Día (Spanish Wordle)."""

from palabra_solver.feedback import GRAY, GREEN, YELLOW, pattern, pattern_to_str
from palabra_solver.model import Solver, Strategy, best_guess, expected_entropy, partition
from palabra_solver.words import WordleWordsHandler

__all__ = [
    "GRAY",
    "GREEN",
    "YELLOW",
    "Solver",
    "Strategy",
    "WordleWordsHandler",
    "best_guess",
    "expected_entropy",
    "partition",
    "pattern",
    "pattern_to_str",
]
