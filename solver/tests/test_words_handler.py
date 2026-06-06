import os
from pathlib import Path

import pytest

from solver import default_dictionary_path
from solver.data import WordleWordsHandler

LEMARIO = default_dictionary_path()

pytestmark = pytest.mark.timeout(10)


class TestStripAccents:
    def test_strip_accents(self) -> None:
        assert WordleWordsHandler.strip_accents("abacá") == "abaca"
        assert WordleWordsHandler.strip_accents("Ábaco") == "Abaco"


class TestNormalize:
    def test_normalize_strips_accents(self) -> None:
        assert WordleWordsHandler.normalize("abacá", length=5) == "abaca"
        assert WordleWordsHandler.normalize("Ábaco", length=5) == "abaco"

    def test_normalize_rejects_hyphens_and_spaces(self) -> None:
        assert WordleWordsHandler.normalize("a-") is None
        assert WordleWordsHandler.normalize("ab aeterno") is None
        assert WordleWordsHandler.normalize("semi-conductor") is None

    def test_normalize_rejects_wrong_length(self) -> None:
        assert WordleWordsHandler.normalize("aba", length=5) is None
        assert WordleWordsHandler.normalize("ababa", length=5) == "ababa"


class TestWordleWordsHandlerLoad:
    def test_load_deduplicates_after_normalization(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abacá\nabajo\nabacá\n", encoding="utf-8")
        handler = WordleWordsHandler(dictionary, length=5).load()
        assert handler.words == ("abaca", "abajo")
        assert WordleWordsHandler(dictionary, length=5).cache_path().is_file()

    def test_load_uses_pickle_when_cache_is_fresher_than_source(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abacá\nabajo\n", encoding="utf-8")
        handler = WordleWordsHandler(dictionary, length=5)

        handler.load()
        cache = handler.cache_path()
        dictionary.write_text("onlybadwords\n", encoding="utf-8")

        source_mtime = dictionary.stat().st_mtime
        os.utime(cache, (source_mtime + 10, source_mtime + 10))

        handler = WordleWordsHandler(dictionary, length=5).load()
        assert handler.words == ("abaca", "abajo")

    @pytest.mark.skipif(not LEMARIO.exists(), reason="lemario file not available")
    def test_load_real_dictionary(self) -> None:
        words = WordleWordsHandler(LEMARIO, length=5).load().words
        assert len(words) > 1000
        assert all(len(word) == 5 for word in words)
        assert "abaca" in words or "abajo" in words
