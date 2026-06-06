import pytest

from solver.model import ThresholdBellmanModel

pytestmark = pytest.mark.timeout(10)


class TestThresholdBellmanValue:
    def test_value_for_singleton_is_one(self) -> None:
        words = ("abaca", "abajo", "abril")
        model = ThresholdBellmanModel(words, persist=False, show_progress=False)
        assert model.value(("abril",)) == 1.0

    def test_value_rejects_large_belief(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        model = ThresholdBellmanModel(words, persist=False, show_progress=False, threshold=3)
        with pytest.raises(ValueError, match="requires"):
            model.value(words)


class TestThresholdBellmanBestGuess:
    def test_best_guess_returns_word_from_pool(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        model = ThresholdBellmanModel(words, persist=False, show_progress=False, threshold=5)
        guess = model.best_guess(words, words)
        assert guess in words

    def test_large_belief_uses_entropy(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        model = ThresholdBellmanModel(words, persist=False, show_progress=False, threshold=3)
        guess = model.best_guess(words, words)
        assert guess in words


class TestThresholdBellmanWarmCache:
    def test_warm_cache_fills_reachable_beliefs(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        model = ThresholdBellmanModel(words, persist=False, show_progress=False, threshold=5)
        solved = model.warm_cache(words)
        assert solved > 0
        assert model.cached_beliefs >= len(words) + 1
        assert model.value(words) > 0
