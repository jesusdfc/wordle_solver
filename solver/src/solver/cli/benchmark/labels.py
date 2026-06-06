"""Shared label and parameter helpers for results.json and plots."""

from __future__ import annotations

from typing import Any

from solver.cli.benchmark.config import DEFAULT_BELIEF_THRESHOLD
from solver.cli.benchmark.types import StrategyReport


def benchmark_report_key(strategy_id: str, belief_threshold: int | None) -> str:
    if belief_threshold is not None and "bellman" in strategy_id:
        return f"{strategy_id}@{belief_threshold}"
    return strategy_id


def stats_report_key(stats: dict[str, Any]) -> str:
    if stats.get("report_key"):
        return str(stats["report_key"])
    strategy_id = stats["strategy"]
    threshold = stats.get("belief_threshold")
    if threshold is None and strategy_id in (
        "entropy-hard-bellman",
        "entropy-threshold-bellman",
    ):
        threshold = DEFAULT_BELIEF_THRESHOLD
    return benchmark_report_key(strategy_id, threshold)


def report_belief_threshold(report: StrategyReport) -> int:
    return report.belief_threshold or DEFAULT_BELIEF_THRESHOLD


def benchmark_strategy_params(
    strategy_id: str,
    *,
    belief_threshold: int = DEFAULT_BELIEF_THRESHOLD,
) -> dict[str, str]:
    """Human-readable parameter summary for benchmark tables and results.json."""
    if strategy_id == "full-entropy":
        return {
            "hard": "no",
            "threshold": "—",
            "probes": "full dict",
        }
    if strategy_id == "fixed-entropy":
        return {
            "hard": "no",
            "threshold": "—",
            "probes": "full dict",
        }
    if strategy_id == "entropy-hard-bellman":
        return {
            "hard": "yes",
            "threshold": str(belief_threshold),
            "probes": "candidates only",
        }
    if strategy_id == "entropy-threshold-bellman":
        return {
            "hard": "no",
            "threshold": str(belief_threshold),
            "probes": "full dict",
        }
    return {
        "hard": "—",
        "threshold": "—",
        "probes": "—",
    }


def plot_label(
    *,
    strategy_id: str,
    label: str,
    belief_threshold: int | None = None,
) -> str:
    """X-axis label with distinguishing parameter, e.g. 'Entropy + hard Bellman (20)'."""
    if strategy_id in ("entropy-hard-bellman", "entropy-threshold-bellman"):
        if belief_threshold is not None:
            return f"{label} ({belief_threshold})"
    return label


def benchmark_plot_label(report: StrategyReport) -> str:
    return plot_label(
        strategy_id=report.strategy_id,
        label=report.label,
        belief_threshold=report.belief_threshold,
    )


def stats_plot_label(stats: dict[str, Any]) -> str:
    return plot_label(
        strategy_id=stats["strategy"],
        label=stats["label"],
        belief_threshold=stats.get("belief_threshold"),
    )
