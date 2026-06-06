import pytest

from solver.model import EntropyModel, OpenerHardBellmanModel, OpenerThresholdBellmanModel
from solver.strategies import WordleStrategies

pytestmark = pytest.mark.timeout(10)


class TestWordleStrategies:
    def test_lists_benchmark_strategies(self) -> None:
        assert WordleStrategies.ids() == (
            "full-entropy",
            "fixed-entropy",
            "entropy-threshold-bellman",
            "entropy-hard-bellman@20",
            "entropy-hard-bellman@50",
            "entropy-hard-bellman@100",
        )

    def test_list_json_shape(self) -> None:
        items = WordleStrategies.list()
        assert len(items) == 6
        assert items[1]["requires_opening_word"] is True
        threshold = next(
            item for item in items if item["id"] == "entropy-threshold-bellman"
        )
        assert threshold["warning"]
        assert threshold["belief_threshold"] == 20
        assert threshold["highlight"] == "best"
        fast = next(item for item in items if item["id"] == "entropy-hard-bellman@50")
        assert fast["highlight"] == "fast"

    def test_hard_bellman_threshold_variants(self) -> None:
        for threshold in (20, 50, 100):
            spec = WordleStrategies.get(f"entropy-hard-bellman@{threshold}")
            assert spec.belief_threshold == threshold


class TestEntropyFirstWord:
    def test_fixed_entropy_uses_first_word_on_turn_one(self) -> None:
        words = ("cario", "abril", "tomar", "acero")
        model = EntropyModel(pattern_table=None, first_word="cario", all_words=words)
        assert model.best_guess(words, words, history=()) == "cario"

    def test_fixed_entropy_strategy(self) -> None:
        words = ("cario", "abril", "tomar")
        model = WordleStrategies.create_model(
            "fixed-entropy",
            all_words=words,
            persist=False,
            show_progress=False,
        )
        assert isinstance(model, EntropyModel)
        assert model.best_guess(words, words, history=()) == WordleStrategies.DEFAULT_OPENING_WORD


class TestHybridModel:
    def test_hard_bellman_after_first_guess(self) -> None:
        words = ("abaca", "abajo", "abril")
        model = WordleStrategies.create_model(
            "entropy-hard-bellman@50",
            all_words=words,
            persist=False,
            show_progress=False,
        )
        assert isinstance(model, OpenerHardBellmanModel)
        guess = model.best_guess(("abril",), words, history=("cario",))
        assert guess == "abril"

    def test_threshold_bellman_after_first_guess(self) -> None:
        words = ("abaca", "abajo", "abril")
        model = WordleStrategies.create_model(
            "entropy-threshold-bellman",
            all_words=words,
            persist=False,
            show_progress=False,
        )
        assert isinstance(model, OpenerThresholdBellmanModel)
        guess = model.best_guess(("abril",), words, history=("cario",))
        assert guess in words
