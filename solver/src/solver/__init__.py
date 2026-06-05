"""Optimal solver for La Palabra del Día (Spanish Wordle)."""

from pathlib import Path

from solver.agent import WordleAgent
from solver.belief import BeliefState
from solver.data import PatternTable, TableLookupPersistor, WordleWordsHandler, get_cache_dir
from solver.env import WordleEnv, WordleObservation
from solver.model import WordleModel

__all__ = [
    "BeliefState",
    "PatternTable",
    "TableLookupPersistor",
    "WordleAgent",
    "WordleEnv",
    "WordleModel",
    "WordleObservation",
    "WordleWordsHandler",
    "default_data_dir",
    "default_dictionary_path",
    "get_cache_dir",
]


def default_dictionary_path() -> Path:
    """Return the lemario path at the repository root."""
    return Path(__file__).resolve().parents[3] / "data" / "lemario-general-del-espanol.txt"


def default_data_dir() -> Path:
    """Return the shared data directory at the repository root."""
    return default_dictionary_path().parent
