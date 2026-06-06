"""Benchmark results.json cache load/save."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from solver.cli.benchmark.config import BenchmarkConfig, RESULTS_FILENAME
from solver.cli.benchmark.labels import stats_report_key
from solver.cli.benchmark.types import GameResult, StrategyReport


def results_path(output_dir: Path) -> Path:
    return output_dir / RESULTS_FILENAME


def load_results(path: Path) -> dict[str, Any]:
    """Load a benchmark summary from *results.json*."""
    if not path.is_file():
        raise FileNotFoundError(f"benchmark results not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_results(output_dir: Path, summary: dict[str, Any]) -> Path:
    path = results_path(output_dir)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return path


def _cache_config_matches(
    cached: dict[str, Any],
    secrets: tuple[str, ...],
    config: BenchmarkConfig,
    *,
    dictionary_size: int,
) -> bool:
    return (
        cached.get("dictionary_size") == dictionary_size
        and cached.get("benchmark_words") == list(secrets)
        and cached.get("max_guesses") == config.max_guesses
        and cached.get("fixed_opener") == config.fixed_opener
    )


def _can_reuse_strategy_stats(stats: dict[str, Any], secrets: tuple[str, ...]) -> bool:
    games = stats.get("games")
    if not games or len(games) != len(secrets):
        return False
    return [game["secret"] for game in games] == list(secrets)


def strategy_stats_to_report(stats: dict[str, Any]) -> StrategyReport:
    games = [
        GameResult(
            secret=game["secret"],
            guesses=game["guesses"],
            solved=game["solved"],
        )
        for game in stats["games"]
    ]
    return StrategyReport(
        strategy_id=stats["strategy"],
        label=stats["label"],
        games=games,
        first_word=stats.get("first_word", ""),
        elapsed_seconds=float(stats.get("elapsed_seconds", 0)),
        belief_threshold=stats.get("belief_threshold"),
    )


def load_cached_strategy_reports(
    output_dir: Path,
    secrets: tuple[str, ...],
    config: BenchmarkConfig,
    *,
    dictionary_size: int,
) -> dict[str, StrategyReport]:
    """Return reusable strategy reports from *results.json*, keyed by report id."""
    path = results_path(output_dir)
    if not path.is_file():
        return {}

    try:
        cached = load_results(path)
    except json.JSONDecodeError:
        return {}

    if not _cache_config_matches(cached, secrets, config, dictionary_size=dictionary_size):
        return {}

    reports: dict[str, StrategyReport] = {}
    for stats in cached.get("strategies", []):
        strategy_id = stats.get("strategy")
        if not strategy_id or not _can_reuse_strategy_stats(stats, secrets):
            continue
        reports[stats_report_key(stats)] = strategy_stats_to_report(stats)
    return reports
