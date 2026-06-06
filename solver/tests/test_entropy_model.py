import pytest

from solver.model import WordleModel

pytestmark = pytest.mark.timeout(10)


class TestEntropyPartition:
    def test_partition_groups_candidates(self) -> None:
        candidates = ("abaca", "abajo", "abano")
        buckets = WordleModel().partition(candidates, "abaca")
        assert sum(len(bucket) for bucket in buckets.values()) == len(candidates)


class TestEntropyScore:
    def test_expected_entropy_is_zero_for_single_candidate(self) -> None:
        assert WordleModel().expected_entropy("abaca", ("abaca",)) == 0.0


class TestEntropyBestGuess:
    def test_best_guess_returns_only_candidate(self) -> None:
        model = WordleModel()
        assert model.best_guess(("abaca",)) == "abaca"
