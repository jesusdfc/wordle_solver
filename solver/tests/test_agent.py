import pytest

from solver.agent import WordleAgent

pytestmark = pytest.mark.timeout(10)


class TestWordleAgentEntropy:
    def test_agent_solves_simple_secret(self) -> None:
        words = ("abaca", "abajo", "abano", "abril", "abono")
        agent = WordleAgent(words, strategy="full-entropy")
        guesses = agent.solve("abril", max_guesses=6)
        assert guesses[-1] == "abril"
        assert len(guesses) <= 6


class TestWordleAgentHybrid:
    def test_entropy_threshold_bellman_solves_small_dictionary(self) -> None:
        words = ("abaca", "abajo", "abano", "abril", "abono")
        agent = WordleAgent(words, strategy="entropy-threshold-bellman", show_progress=False)
        guesses = agent.solve("abono", max_guesses=6)
        assert guesses[-1] == "abono"
        assert len(guesses) <= 6
