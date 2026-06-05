from pathlib import Path

import pytest

from palabra_solver.agent import Strategy, WordleAgent
from palabra_solver.belief import BeliefState
from palabra_solver.data import WordleWordsHandler
from palabra_solver.env import WordleEnv

LEMARIO = Path(__file__).resolve().parents[1] / "lemario-general-del-espanol.txt"


class TestWordleWordsHandler:
    def test_strip_accents(self) -> None:
        assert WordleWordsHandler.strip_accents("abacá") == "abaca"
        assert WordleWordsHandler.strip_accents("Ábaco") == "Abaco"

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

    def test_load_deduplicates_after_normalization(self) -> None:
        handler = WordleWordsHandler(
            Path(__file__).parent / "fixtures" / "sample_words.txt",
            length=5,
        ).load()
        assert handler.words == ("abaca", "abajo")

    @pytest.mark.skipif(not LEMARIO.exists(), reason="lemario file not available")
    def test_load_real_dictionary(self) -> None:
        words = WordleWordsHandler(LEMARIO, length=5).load().words
        assert len(words) > 1000
        assert all(len(word) == 5 for word in words)
        assert "abaca" in words or "abajo" in words


class TestWordleEnv:
    def test_all_green(self) -> None:
        assert WordleEnv.pattern("abaca", "abaca") == sum(
            WordleEnv.GREEN * (3**i) for i in range(5)
        )

    def test_duplicate_letters(self) -> None:
        secret = "aabbc"
        guess = "aaaab"
        value = WordleEnv.pattern(secret, guess)
        codes = [(value // (3**index)) % 3 for index in range(5)]
        assert codes == [
            WordleEnv.GREEN,
            WordleEnv.GREEN,
            WordleEnv.GRAY,
            WordleEnv.GRAY,
            WordleEnv.YELLOW,
        ]

    def test_reset_and_step(self) -> None:
        words = ("abaca", "abajo", "abril")
        env = WordleEnv(words)
        obs = env.reset(secret="abril")
        assert obs.turn == 0
        assert obs.guesses == ()

        obs, reward, done, info = env.step("abaca")
        assert obs.turn == 1
        assert obs.guesses == ("abaca",)
        assert info["pattern"] == WordleEnv.pattern("abril", "abaca")
        assert reward == 0.0
        assert done is False

    def test_step_wins(self) -> None:
        env = WordleEnv(("abril",))
        env.reset(secret="abril")
        _, reward, done, info = env.step("abril")
        assert reward == 1.0
        assert done is True
        assert info["won"] is True


class TestBeliefState:
    def test_update_filters_candidates(self) -> None:
        belief = BeliefState(("abaca", "abajo", "abril"))
        pattern = WordleEnv.pattern("abril", "abaca")
        belief.update("abaca", pattern)
        assert belief.candidates == ("abril",)

    def test_is_solved(self) -> None:
        belief = BeliefState(("abril",))
        assert belief.is_solved() is True


class TestWordleAgent:
    def test_partition_groups_candidates(self) -> None:
        candidates = ("abaca", "abajo", "abano")
        buckets = WordleAgent.partition(candidates, "abaca")
        assert sum(len(bucket) for bucket in buckets.values()) == len(candidates)

    def test_expected_entropy_is_zero_for_single_candidate(self) -> None:
        assert WordleAgent.expected_entropy("abaca", ("abaca",)) == 0.0

    def test_best_guess_returns_only_candidate(self) -> None:
        assert WordleAgent.best_guess(("abaca",)) == "abaca"

    def test_agent_solves_simple_secret(self) -> None:
        words = ("abaca", "abajo", "abano", "abril", "abono")
        agent = WordleAgent(words)
        guesses = agent.solve("abril", max_guesses=6)
        assert guesses[-1] == "abril"
        assert len(guesses) <= 6

    def test_minimax_prefers_balanced_split(self) -> None:
        candidates = ("abcaa", "abcbb", "abccc")
        guess = WordleAgent.best_guess(candidates, candidates, strategy=Strategy.MINIMAX)
        assert guess in candidates
