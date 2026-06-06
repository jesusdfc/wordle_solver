import pytest

from solver.model import HardBellmanModel

pytestmark = pytest.mark.timeout(10)


class TestHardBellmanBestGuess:
    def test_best_guess_only_from_candidates(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        model = HardBellmanModel(words, persist=False, show_progress=False, threshold=5)
        guess = model.best_guess(("aabbb", "aaccc"), words)
        assert guess in ("aabbb", "aaccc")

    def test_large_belief_uses_entropy(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        model = HardBellmanModel(words, persist=False, show_progress=False, threshold=3)
        guess = model.best_guess(words, words)
        assert guess in words


class TestHardBellmanValue:
    def test_value_for_singleton_is_one(self) -> None:
        words = ("abaca", "abajo", "abril")
        model = HardBellmanModel(words, persist=False, show_progress=False)
        assert model.value(("abril",)) == 1.0
