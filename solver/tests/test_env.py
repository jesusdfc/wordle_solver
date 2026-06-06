import pytest

from solver.env import WordleEnv

pytestmark = pytest.mark.timeout(10)


class TestPattern:
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


class TestWordleEnvStep:
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
