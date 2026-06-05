"""Precomputed pattern lookup table for Wordle feedback."""

from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from pathlib import Path

from solver.data.words import WordleWordsHandler
from solver.env import WordleEnv


@dataclass(frozen=True)
class PatternTable:
    """O(1) lookup for feedback patterns over a fixed word list."""

    words: tuple[str, ...]
    _patterns: bytes
    _index: dict[str, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        expected = len(self.words) ** 2
        if len(self._patterns) != expected:
            raise ValueError(f"pattern buffer length {len(self._patterns)} != {len(self.words)}²")
        object.__setattr__(
            self,
            "_index",
            {word: index for index, word in enumerate(self.words)},
        )

    @classmethod
    def build(cls, words: tuple[str, ...]) -> PatternTable:
        """Compute the full secret × guess pattern matrix."""
        count = len(words)
        patterns = bytearray(count * count)
        for secret_index, secret in enumerate(words):
            row_offset = secret_index * count
            for guess_index, guess in enumerate(words):
                patterns[row_offset + guess_index] = WordleEnv.pattern(secret, guess)
        return cls(words=words, _patterns=bytes(patterns))

    def pattern(self, secret: str, guess: str) -> int:
        """Return feedback for `guess` when the answer is `secret`."""
        try:
            secret_index = self._index[secret]
            guess_index = self._index[guess]
        except KeyError:
            return WordleEnv.pattern(secret, guess)
        return self._patterns[secret_index * len(self.words) + guess_index]


class TableLookupPersistor:
    """Build, cache, and load pattern lookup tables under ``data/``."""

    def __init__(
        self,
        dictionary_path: Path | str,
        length: int = 5,
        *,
        data_dir: Path | str | None = None,
    ) -> None:
        self.dictionary_path = Path(dictionary_path)
        self.length = length
        self.data_dir = Path(data_dir) if data_dir is not None else self.dictionary_path.parent

    def cache_path(self) -> Path:
        """Path to the cached pattern table for this word length."""
        return self.data_dir / f"word_{self.length}_dict.pickle"

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

    def load(self) -> PatternTable:
        """Load the pattern table, building and caching it when needed."""
        words = WordleWordsHandler(self.dictionary_path, length=self.length).load().words
        cached = self._load_from_cache()
        if cached is not None and cached.words == words:
            return cached

        table = PatternTable.build(words)
        self._save_cache(table)
        return table
