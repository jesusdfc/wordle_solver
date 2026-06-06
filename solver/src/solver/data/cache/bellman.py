"""Persist Bellman value-function memoization to disk."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

from solver.data.cache.base import get_cache_dir
from solver.data.words import WordleWordsHandler


@dataclass
class BellmanValueCache:
    """Serialized Bellman DP memo for a fixed word list."""

    words: tuple[str, ...]
    values: dict[tuple[str, ...], float]


class ValueFunctionPersistor:
    """Load and save ``{cache_tag}_{length}_value_function.pickle`` caches."""

    def __init__(
        self,
        dictionary_path: Path | str,
        length: int = 5,
        *,
        data_dir: Path | str | None = None,
        cache_tag: str = "threshold_bellman",
    ) -> None:
        self.dictionary_path = Path(dictionary_path)
        self.length = length
        self.cache_tag = cache_tag
        self.data_dir = (
            Path(data_dir) if data_dir is not None else get_cache_dir(self.dictionary_path.parent)
        )

    def cache_path(self) -> Path:
        return self.data_dir / f"{self.cache_tag}_{self.length}_value_function.pickle"

    def _source_mtime(self) -> float:
        mtimes = [self.dictionary_path.stat().st_mtime]
        words_cache = WordleWordsHandler(self.dictionary_path, length=self.length).cache_path()
        if words_cache.is_file():
            mtimes.append(words_cache.stat().st_mtime)
        lookup_cache = self.data_dir / f"entropy_{self.length}_lookup_table.pickle"
        if lookup_cache.is_file():
            mtimes.append(lookup_cache.stat().st_mtime)
        return max(mtimes)

    def load(self, words: tuple[str, ...]) -> dict[tuple[str, ...], float]:
        cache = self.cache_path()
        if not cache.is_file() or not self.dictionary_path.is_file():
            return {}
        if cache.stat().st_mtime < self._source_mtime():
            return {}
        try:
            with cache.open("rb") as handle:
                payload = pickle.load(handle)
        except (pickle.UnpicklingError, ModuleNotFoundError, AttributeError):
            return {}
        if not isinstance(payload, BellmanValueCache):
            return {}
        if payload.words != words:
            return {}
        return dict(payload.values)

    def save(self, words: tuple[str, ...], values: dict[tuple[str, ...], float]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        payload = BellmanValueCache(words=words, values=dict(values))
        with self.cache_path().open("wb") as handle:
            pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)
