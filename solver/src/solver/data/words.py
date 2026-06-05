"""Load and normalize Spanish dictionary words for Wordle."""

from __future__ import annotations

import pickle
import re
import unicodedata
from collections.abc import Callable, Iterator
from pathlib import Path

_DISALLOWED_RE = re.compile(r"[\s\-0-9'\".,;:/\\()[\]{}]")
_VALID_CHARS_RE = re.compile(r"^[a-zñ]+$")


class WordleWordsHandler:
    """Load a dictionary file and expose normalized Wordle-ready words."""

    def __init__(
        self,
        path: Path | str,
        length: int = 5,
        *,
        encoding: str = "utf-8",
    ) -> None:
        self.path = Path(path)
        self.length = length
        self.encoding = encoding
        self._words: tuple[str, ...] = ()
        self._loaded = False

    @staticmethod
    def strip_accents(text: str) -> str:
        """Remove diacritics from text (e.g. abacá → abaca)."""
        decomposed = unicodedata.normalize("NFD", text)
        return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")

    @staticmethod
    def normalize(raw: str, *, length: int | None = None) -> str | None:
        """Return a normalized word or None if the entry is not playable."""
        text = raw.strip().lower()
        if not text:
            return None
        if _DISALLOWED_RE.search(text):
            return None
        if not all(char.isalpha() for char in text):
            return None

        normalized = WordleWordsHandler.strip_accents(text)
        if not _VALID_CHARS_RE.fullmatch(normalized):
            return None
        if length is not None and len(normalized) != length:
            return None
        return normalized

    def cache_path(self) -> Path:
        """Path to the pickled word list for this dictionary and length."""
        return self.path.parent / f"words_{self.length}.pickle"

    def _load_from_source(self) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        with self.path.open(encoding=self.encoding) as handle:
            for line in handle:
                word = self.normalize(line, length=self.length)
                if word is not None:
                    seen.setdefault(word, None)
        return tuple(seen.keys())

    def _load_from_cache(self) -> tuple[str, ...] | None:
        cache = self.cache_path()
        if not cache.is_file() or not self.path.is_file():
            return None
        if cache.stat().st_mtime < self.path.stat().st_mtime:
            return None
        with cache.open("rb") as handle:
            words = pickle.load(handle)
        if not isinstance(words, tuple) or not all(isinstance(word, str) for word in words):
            return None
        return words

    def _save_cache(self, words: tuple[str, ...]) -> None:
        with self.cache_path().open("wb") as handle:
            pickle.dump(words, handle)

    def load(self) -> WordleWordsHandler:
        """Read the dictionary file and populate the word list."""
        cached = self._load_from_cache()
        if cached is not None:
            self._words = cached
        else:
            self._words = self._load_from_source()
            self._save_cache(self._words)
        self._loaded = True
        return self

    @property
    def words(self) -> tuple[str, ...]:
        if not self._loaded:
            self.load()
        return self._words

    def __iter__(self) -> Iterator[str]:
        yield from self.words

    def __len__(self) -> int:
        return len(self.words)

    def __contains__(self, word: str) -> bool:
        normalized = self.normalize(word, length=self.length)
        return normalized is not None and normalized in self._words

    def filter(self, predicate: Callable[[str], bool]) -> tuple[str, ...]:
        return tuple(word for word in self.words if predicate(word))
