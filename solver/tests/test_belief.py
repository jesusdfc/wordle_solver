import pytest

from solver.belief import BeliefState
from solver.env import WordleEnv

pytestmark = pytest.mark.timeout(10)


class TestBeliefUpdate:
    def test_update_filters_candidates(self) -> None:
        belief = BeliefState(("abaca", "abajo", "abril"))
        pattern = WordleEnv.pattern("abril", "abaca")
        belief.update("abaca", pattern)
        assert belief.candidates == ("abril",)


class TestBeliefSolved:
    def test_is_solved(self) -> None:
        belief = BeliefState(("abril",))
        assert belief.is_solved() is True
