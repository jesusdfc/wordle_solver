from pathlib import Path

import pytest

from solver.data import ValueFunctionPersistor

pytestmark = pytest.mark.timeout(10)


class TestBellmanValueFunctionCache:
    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abaca\nabajo\nabril\n", encoding="utf-8")
        words = ("abaca", "abajo", "abril")
        values = {words: 2.5, ("abril",): 1.0}

        persistor = ValueFunctionPersistor(dictionary, length=5, data_dir=tmp_path)
        persistor.save(words, values)

        cache = tmp_path / "threshold_bellman_5_value_function.pickle"
        assert cache.is_file()
        assert persistor.load(words) == values
        assert persistor.load(("abaca", "abajo")) == {}
