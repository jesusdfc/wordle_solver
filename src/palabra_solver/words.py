"""Load and normalize Spanish dictionary words for Wordle."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable, Iterator
from pathlib import Path

_DISALLOWED_RE = re.compile(r"[\s\-0-9'\".,;:/\\()[\]{}]")
_VALID_CHARS_RE = re.compile(r"^[a-zñ]+$")


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


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
    def normalize(raw: str, *, length: int | None = None) -> str | None:
        """Return a normalized word or None if the entry is not playable."""
        text = raw.strip().lower()
        if not text:
            return None
        if _DISALLOWED_RE.search(text):
            return None
        if not all(char.isalpha() for char in text):
            return None

        normalized = _strip_accents(text)
        if not _VALID_CHARS_RE.fullmatch(normalized):
            return None
        if length is not None and len(normalized) != length:
            return None
        return normalized

    def load(self) -> WordleWordsHandler:
        """Read the dictionary file and populate the word list."""
        seen: dict[str, None] = {}
        with self.path.open(encoding=self.encoding) as handle:
            for line in handle:
                word = self.normalize(line, length=self.length)
                if word is not None:
                    seen.setdefault(word, None)
        self._words = tuple(seen.keys())
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
