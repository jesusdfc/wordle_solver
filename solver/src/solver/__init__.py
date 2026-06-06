"""Optimal solver for La Palabra del Día (Spanish Wordle)."""

from pathlib import Path

from solver.agent import WordleAgent
from solver.belief import BeliefState
from solver.data import PatternTable, TableLookupPersistor, WordleWordsHandler, get_cache_dir
from solver.env import WordleEnv, WordleObservation
from solver.model import EntropyModel, WordleModel
from solver.strategies import WordleStrategies

__all__ = [
    "BeliefState",
    "PatternTable",
    "TableLookupPersistor",
    "EntropyModel",
    "WordleAgent",
    "WordleEnv",
    "WordleModel",
    "WordleObservation",
    "WordleStrategies",
    "WordleWordsHandler",
    "default_cache_dir",
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


def default_cache_dir() -> Path:
    """Return the default pickle cache directory (``data/cache/`` at repo root)."""
    return get_cache_dir(default_data_dir())
