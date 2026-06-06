import pytest

from solver.data.patterns import PatternTable
from solver.model.entropy import EntropyModel

pytestmark = pytest.mark.timeout(10)


class TestPatternTablePartitionGroups:
    def test_partition_groups_matches_base_partition(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        table = PatternTable.build(words, show_progress=False)
        candidates = words
        guess = "bbbbb"

        groups = table.partition_groups(candidates, guess)
        model = EntropyModel(pattern_table=table)
        base_groups = [
            model._candidate_key(bucket)
            for bucket in model.partition(candidates, guess).values()
        ]

        assert sorted(groups) == sorted(base_groups)


class TestPatternTableEntropyScores:
    def test_entropy_scores_match_loop(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        table = PatternTable.build(words, show_progress=False)
        model = EntropyModel(pattern_table=table)
        slow = [model.expected_entropy(guess, words) for guess in words]
        fast = table.entropy_scores(words, words)
        assert slow == pytest.approx(list(fast))

    def test_vectorized_best_guess_matches_loop(self) -> None:
        words = ("aabbb", "aaccc", "bbbbb", "ccccc")
        table = PatternTable.build(words, show_progress=False)
        fast = EntropyModel(pattern_table=table)
        slow = EntropyModel()
        assert fast.best_guess(words, words) == slow.best_guess(words, words)
