from pathlib import Path

import pytest

from palabra_solver.feedback import GRAY, GREEN, YELLOW, pattern
from palabra_solver.model import Solver, Strategy, best_guess, expected_entropy, partition
from palabra_solver.words import WordleWordsHandler

LEMARIO = Path(__file__).resolve().parents[1] / "lemario-general-del-espanol.txt"


class TestWordleWordsHandler:
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


class TestFeedback:
    def test_all_green(self) -> None:
        assert pattern("abaca", "abaca") == sum(GREEN * (3**i) for i in range(5))

    def test_duplicate_letters(self) -> None:
        # Two a's in the secret: only two a's in the guess can be marked non-gray.
        secret = "aabbc"
        guess = "aaaab"
        value = pattern(secret, guess)
        codes = [(value // (3**index)) % 3 for index in range(5)]
        assert codes == [GREEN, GREEN, GRAY, GRAY, YELLOW]


class TestModel:
    def test_partition_groups_candidates(self) -> None:
        candidates = ("abaca", "abajo", "abano")
        buckets = partition(candidates, "abaca")
        assert sum(len(bucket) for bucket in buckets.values()) == len(candidates)

    def test_expected_entropy_is_zero_for_single_candidate(self) -> None:
        assert expected_entropy("abaca", ("abaca",)) == 0.0

    def test_best_guess_returns_only_candidate(self) -> None:
        assert best_guess(("abaca",)) == "abaca"

    def test_solver_solves_simple_secret(self) -> None:
        words = ("abaca", "abajo", "abano", "abril", "abono")
        solver = Solver(words)
        guesses = solver.solve("abril", max_guesses=6)
        assert guesses[-1] == "abril"
        assert len(guesses) <= 6

    def test_minimax_prefers_balanced_split(self) -> None:
        candidates = ("abcaa", "abcbb", "abccc")
        guess = best_guess(candidates, candidates, strategy=Strategy.MINIMAX)
        assert guess in candidates
