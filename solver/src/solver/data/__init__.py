"""Dictionary loading and precomputed pattern lookup."""

from solver.data.cache import get_cache_dir
from solver.data.patterns import PatternTable, TableLookupPersistor
from solver.data.words import WordleWordsHandler

__all__ = [
    "PatternTable",
    "TableLookupPersistor",
    "WordleWordsHandler",
    "get_cache_dir",
]
