"""Benchmark suite: run strategies, cache results, and plot from results.json."""

from solver.cli.benchmark.cli import register, run
from solver.cli.benchmark.config import BENCHMARK_STRATEGIES, BenchmarkConfig, BenchmarkStrategy
from solver.cli.benchmark.labels import (
    benchmark_plot_label,
    benchmark_report_key,
    benchmark_strategy_params,
)
from solver.cli.benchmark.plots import plot_benchmark, plot_benchmark_dir, plot_benchmark_file
from solver.cli.benchmark.runner import run_study, summarize_report
from solver.cli.benchmark.types import GameResult, StrategyReport
from solver.cli.benchmark.words import load_or_create_benchmark_words, subsample_secrets

__all__ = [
    "BENCHMARK_STRATEGIES",
    "BenchmarkConfig",
    "BenchmarkStrategy",
    "GameResult",
    "StrategyReport",
    "benchmark_plot_label",
    "benchmark_report_key",
    "benchmark_strategy_params",
    "load_or_create_benchmark_words",
    "plot_benchmark",
    "plot_benchmark_dir",
    "plot_benchmark_file",
    "register",
    "run",
    "run_study",
    "subsample_secrets",
    "summarize_report",
]
