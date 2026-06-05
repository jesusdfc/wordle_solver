import os
from pathlib import Path

import pytest

from solver import default_dictionary_path
from solver.agent import WordleAgent
from solver.belief import BeliefState
from solver.data import TableLookupPersistor, WordleWordsHandler
from solver.env import WordleEnv
from solver.model import Strategy, WordleModel

LEMARIO = default_dictionary_path()


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

    def test_load_deduplicates_after_normalization(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abacá\nabajo\nabacá\n", encoding="utf-8")
        handler = WordleWordsHandler(dictionary, length=5).load()
        assert handler.words == ("abaca", "abajo")
        assert (tmp_path / "words_5.pickle").is_file()

    def test_load_uses_pickle_when_cache_is_fresher_than_source(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abacá\nabajo\n", encoding="utf-8")
        cache = tmp_path / "words_5.pickle"

        WordleWordsHandler(dictionary, length=5).load()
        dictionary.write_text("onlybadwords\n", encoding="utf-8")

        source_mtime = dictionary.stat().st_mtime
        os.utime(cache, (source_mtime + 10, source_mtime + 10))

        handler = WordleWordsHandler(dictionary, length=5).load()
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


class TestWordleModel:
    def test_partition_groups_candidates(self) -> None:
        candidates = ("abaca", "abajo", "abano")
        buckets = WordleModel().partition(candidates, "abaca")
        assert sum(len(bucket) for bucket in buckets.values()) == len(candidates)

    def test_expected_entropy_is_zero_for_single_candidate(self) -> None:
        assert WordleModel().expected_entropy("abaca", ("abaca",)) == 0.0

    def test_best_guess_returns_only_candidate(self) -> None:
        model = WordleModel()
        assert model.best_guess(("abaca",)) == "abaca"

    def test_minimax_prefers_balanced_split(self) -> None:
        candidates = ("abcaa", "abcbb", "abccc")
        model = WordleModel(strategy=Strategy.MINIMAX)
        guess = model.best_guess(candidates, candidates)
        assert guess in candidates


class TestWordleAgent:
    def test_agent_solves_simple_secret(self) -> None:
        words = ("abaca", "abajo", "abano", "abril", "abono")
        agent = WordleAgent(words)
        guesses = agent.solve("abril", max_guesses=6)
        assert guesses[-1] == "abril"
        assert len(guesses) <= 6


class TestTableLookupPersistor:
    def test_builds_and_reuses_pattern_cache(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abacá\nabajo\nabril\n", encoding="utf-8")

        persistor = TableLookupPersistor(dictionary, length=5, data_dir=tmp_path)
        table = persistor.load()
        cache = tmp_path / "word_5_dict.pickle"

        assert cache.is_file()
        assert table.pattern("abril", "abaca") == WordleEnv.pattern("abril", "abaca")

        table_again = persistor.load()
        assert table_again.words == table.words
        assert table_again.pattern("abajo", "abril") == table.pattern("abajo", "abril")

    def test_pattern_table_matches_env_for_all_pairs(self, tmp_path: Path) -> None:
        dictionary = tmp_path / "words.txt"
        dictionary.write_text("abaca\nabajo\nabril\n", encoding="utf-8")
        table = TableLookupPersistor(dictionary, length=5, data_dir=tmp_path).load()

        for secret in table.words:
            for guess in table.words:
                assert table.pattern(secret, guess) == WordleEnv.pattern(secret, guess)
