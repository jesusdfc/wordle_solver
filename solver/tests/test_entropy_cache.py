from pathlib import Path

import pytest

from solver.data import TableLookupPersistor
from solver.env import WordleEnv

pytestmark = pytest.mark.timeout(10)


class TestEntropyLookupCache:
    def test_builds_and_reuses_pattern_cache(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abacá\nabajo\nabril\n", encoding="utf-8")

        persistor = TableLookupPersistor(dictionary, length=5, data_dir=tmp_path)
        table = persistor.load(show_progress=False)
        cache = tmp_path / "entropy_5_lookup_table.pickle"

        assert cache.is_file()
        assert table.pattern("abril", "abaca") == WordleEnv.pattern("abril", "abaca")

        table_again = persistor.load(show_progress=False)
        assert table_again.words == table.words
        assert table_again.pattern("abajo", "abril") == table.pattern("abajo", "abril")


class TestEntropyLookupTable:
    def test_pattern_table_matches_env_for_all_pairs(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abaca\nabajo\nabril\n", encoding="utf-8")
        table = TableLookupPersistor(dictionary, length=5, data_dir=tmp_path).load(
            show_progress=False
        )

        for secret in table.words:
            for guess in table.words:
                assert table.pattern(secret, guess) == WordleEnv.pattern(secret, guess)
