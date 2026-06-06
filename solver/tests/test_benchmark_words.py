import json

import pytest

from solver.cli.benchmark import load_or_create_benchmark_words, subsample_secrets

pytestmark = pytest.mark.timeout(10)


class TestBenchmarkWords:
    def test_load_or_create_persists_and_reloads(self, tmp_path) -> None:
        words = tuple(f"word{i}" for i in range(20))
        path = tmp_path / "benchmark_words.json"

        first = load_or_create_benchmark_words(
            path,
            words,
            num_secrets=5,
            seed=7,
        )
        second = load_or_create_benchmark_words(
            path,
            words,
            num_secrets=99,
            seed=99,
        )

        assert first == second
        assert len(first) == 5
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["seed"] == 7
        assert payload["num_secrets"] == 5

    def test_resample_replaces_existing_list(self, tmp_path) -> None:
        words = tuple(f"word{i}" for i in range(20))
        path = tmp_path / "benchmark_words.json"

        first = load_or_create_benchmark_words(path, words, num_secrets=5, seed=1)
        second = load_or_create_benchmark_words(
            path,
            words,
            num_secrets=5,
            seed=2,
            resample=True,
        )

        assert first != second
        assert second == subsample_secrets(words, 5, seed=2)
