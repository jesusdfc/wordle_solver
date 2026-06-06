import json

import pytest

from solver.cli.benchmark.cache import load_cached_strategy_reports
from solver.cli.benchmark.config import BenchmarkConfig
from solver.cli.benchmark.labels import (
    benchmark_plot_label,
    benchmark_report_key,
    benchmark_strategy_params,
)
from solver.cli.benchmark.plots import plot_benchmark
from solver.cli.benchmark.runner import summarize_report
from solver.cli.benchmark.types import GameResult, StrategyReport

pytestmark = pytest.mark.timeout(10)


def _write_results(
    path,
    *,
    secrets: tuple[str, ...],
    strategies: list[dict],
    dictionary_size: int = 5019,
    max_guesses: int = 6,
    fixed_opener: str = "acero",
) -> None:
    path.write_text(
        json.dumps(
            {
                "dictionary_size": dictionary_size,
                "benchmark_words": list(secrets),
                "max_guesses": max_guesses,
                "fixed_opener": fixed_opener,
                "strategies": strategies,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


class TestBenchmarkCache:
    def test_load_cached_strategy_reports_reuses_matching_games(self, tmp_path) -> None:
        secrets = ("abril", "acero", "alces")
        stats = summarize_report(
            StrategyReport(
                strategy_id="full-entropy",
                label="Full entropy",
                games=[
                    GameResult(secret=secrets[0], guesses=3, solved=True),
                    GameResult(secret=secrets[1], guesses=4, solved=True),
                    GameResult(secret=secrets[2], guesses=5, solved=False),
                ],
                first_word="cario",
                elapsed_seconds=1.23,
            )
        )
        _write_results(tmp_path / "results.json", secrets=secrets, strategies=[stats])

        config = BenchmarkConfig(dictionary=tmp_path / "dict.txt", output_dir=tmp_path)
        cached = load_cached_strategy_reports(
            tmp_path,
            secrets,
            config,
            dictionary_size=5019,
        )

        assert set(cached) == {"full-entropy"}
        report = cached["full-entropy"]
        assert report.first_word == "cario"
        assert report.elapsed_seconds == 1.23
        assert len(report.games) == 3
        assert report.games[1].guesses == 4

    def test_cache_miss_when_secrets_change(self, tmp_path) -> None:
        secrets = ("abril", "acero")
        other_secrets = ("abril", "alces")
        stats = summarize_report(
            StrategyReport(
                strategy_id="full-entropy",
                label="Full entropy",
                games=[
                    GameResult(secret=secrets[0], guesses=3, solved=True),
                    GameResult(secret=secrets[1], guesses=4, solved=True),
                ],
                first_word="cario",
            )
        )
        _write_results(tmp_path / "results.json", secrets=secrets, strategies=[stats])

        config = BenchmarkConfig(dictionary=tmp_path / "dict.txt", output_dir=tmp_path)
        cached = load_cached_strategy_reports(
            tmp_path,
            other_secrets,
            config,
            dictionary_size=5019,
        )

        assert cached == {}

    def test_cache_miss_without_per_game_results(self, tmp_path) -> None:
        secrets = ("abril", "acero")
        _write_results(
            tmp_path / "results.json",
            secrets=secrets,
            strategies=[
                {
                    "strategy": "full-entropy",
                    "label": "Full entropy",
                    "first_word": "cario",
                    "count": 2,
                    "mean_guesses": 3.5,
                    "elapsed_seconds": 1.0,
                }
            ],
        )

        config = BenchmarkConfig(dictionary=tmp_path / "dict.txt", output_dir=tmp_path)
        cached = load_cached_strategy_reports(
            tmp_path,
            secrets,
            config,
            dictionary_size=5019,
        )

        assert cached == {}


class TestBenchmarkStrategyParams:
    def test_hard_bellman_params(self) -> None:
        params = benchmark_strategy_params("entropy-hard-bellman", belief_threshold=20)
        assert params["hard"] == "yes"
        assert params["threshold"] == "20"
        assert params["probes"] == "candidates only"

    def test_full_entropy_params(self) -> None:
        params = benchmark_strategy_params("full-entropy")
        assert params["hard"] == "no"
        assert params["threshold"] == "—"

    def test_plot_label_includes_threshold_for_hard_bellman(self) -> None:
        report = StrategyReport(
            strategy_id="entropy-hard-bellman",
            label="Entropy + hard Bellman",
            games=[],
            first_word="cario",
            belief_threshold=20,
        )
        assert benchmark_plot_label(report) == "Entropy + hard Bellman (20)"
        report.belief_threshold = 50
        assert benchmark_plot_label(report) == "Entropy + hard Bellman (50)"

    def test_report_key_distinguishes_thresholds(self) -> None:
        assert benchmark_report_key("entropy-hard-bellman", 20) == "entropy-hard-bellman@20"
        assert benchmark_report_key("entropy-hard-bellman", 50) == "entropy-hard-bellman@50"
        assert benchmark_report_key("full-entropy", None) == "full-entropy"

    def test_plot_label_uses_plain_name_for_fixed_entropy(self) -> None:
        report = StrategyReport(
            strategy_id="fixed-entropy",
            label="Fixed + entropy",
            games=[],
            first_word="acero",
        )
        assert benchmark_plot_label(report) == "Fixed + entropy"

    def test_plot_benchmark_from_summary(self, tmp_path) -> None:
        summary = {
            "secrets_played": 2,
            "strategies": [
                summarize_report(
                    StrategyReport(
                        "full-entropy",
                        "Full entropy",
                        [GameResult("abril", 3, True), GameResult("acero", 4, True)],
                        first_word="cario",
                        elapsed_seconds=1.0,
                    )
                ),
                summarize_report(
                    StrategyReport(
                        "entropy-hard-bellman",
                        "Entropy + hard Bellman",
                        [GameResult("abril", 3, True), GameResult("acero", 3, True)],
                        first_word="cario",
                        elapsed_seconds=2.0,
                        belief_threshold=50,
                    )
                ),
            ],
        }
        plot_path = plot_benchmark(summary, tmp_path)
        assert plot_path == tmp_path / "benchmark.png"
        assert plot_path.is_file()
