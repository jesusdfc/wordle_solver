"""Persist entropy pattern lookup tables to disk."""

from __future__ import annotations

import pickle
from pathlib import Path

from solver.data.cache.base import get_cache_dir
from solver.data.patterns import PatternTable
from solver.data.words import WordleWordsHandler


class TableLookupPersistor:
    """Build, cache, and load pattern lookup tables under ``data/cache/``."""

    def __init__(
        self,
        dictionary_path: Path | str,
        length: int = 5,
        *,
        data_dir: Path | str | None = None,
    ) -> None:
        self.dictionary_path = Path(dictionary_path)
        self.length = length
        self.data_dir = (
            Path(data_dir) if data_dir is not None else get_cache_dir(self.dictionary_path.parent)
        )

    def cache_path(self) -> Path:
        """Path to the cached entropy lookup table for this word length."""
        return self.data_dir / f"entropy_{self.length}_lookup_table.pickle"

    def _source_mtime(self) -> float:
        mtimes = [self.dictionary_path.stat().st_mtime]
        words_cache = WordleWordsHandler(self.dictionary_path, length=self.length).cache_path()
        if words_cache.is_file():
            mtimes.append(words_cache.stat().st_mtime)
        return max(mtimes)

    def _load_from_cache(self) -> PatternTable | None:
        cache = self.cache_path()
        if not cache.is_file() or not self.dictionary_path.is_file():
            return None
        if cache.stat().st_mtime < self._source_mtime():
            return None
        try:
            with cache.open("rb") as handle:
                table = pickle.load(handle)
        except (pickle.UnpicklingError, ModuleNotFoundError, AttributeError):
            return None
        if not isinstance(table, PatternTable):
            return None
        return table

    def _save_cache(self, table: PatternTable) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self.cache_path().open("wb") as handle:
            pickle.dump(table, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self, *, show_progress: bool = True) -> PatternTable:
        """Load the pattern table, building and caching it when needed."""
        words = WordleWordsHandler(self.dictionary_path, length=self.length).load().words
        cached = self._load_from_cache()
        if cached is not None and cached.words == words:
            return cached

        table = PatternTable.build(words, length=self.length, show_progress=show_progress)
        self._save_cache(table)
        return table
