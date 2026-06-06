"""Benchmark CLI entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from solver import default_dictionary_path
from solver.cli.benchmark.cache import RESULTS_FILENAME, results_path
from solver.cli.benchmark.config import (
    DEFAULT_BENCHMARK_WORDS_PATH,
    FIXED_ENTROPY_OPENER,
    BenchmarkConfig,
)
from solver.cli.benchmark.plots import plot_benchmark_dir
from solver.cli.benchmark.runner import run_study
from solver.cli.helpers import load_pattern_table


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "benchmark",
        help="Compare benchmark strategies on every dictionary word",
        description=(
            "Runs full-entropy, fixed-entropy (acero), entropy-threshold-bellman (20), "
            "and entropy-hard-bellman (thresholds 20, 50, 100) on a "
            "fixed secret-word list (100 by default, stored in data/benchmark_words.json). "
            "Uses the full dictionary as the probe pool. "
            "Reuses per-strategy results from outputs/results.json when the benchmark "
            "configuration matches. Writes outputs/benchmark.png and outputs/results.json. "
            "Pass --plot-only to regenerate the plot from an existing results.json."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_dictionary_path().parents[1] / "outputs",
        help=f"Directory for {RESULTS_FILENAME} and benchmark.png (default: outputs/)",
    )
    parser.add_argument(
        "--num-secrets",
        type=int,
        default=100,
        help=(
            "Number of secret words when creating benchmark_words.json "
            "(0 = all dictionary words, default: 100)"
        ),
    )
    parser.add_argument(
        "--benchmark-words",
        type=Path,
        default=DEFAULT_BENCHMARK_WORDS_PATH,
        help="Path to the fixed benchmark secret-word list (default: data/benchmark_words.json)",
    )
    parser.add_argument(
        "--resample-words",
        action="store_true",
        help="Ignore existing benchmark_words.json and sample a new list",
    )
    parser.add_argument(
        "--dictionary-size",
        type=int,
        dest="num_secrets",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--max-secrets",
        type=int,
        default=0,
        help="Play only the first N secrets (0 = all, default)",
    )
    parser.add_argument("--max-guesses", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--fixed-opener",
        default=FIXED_ENTROPY_OPENER,
        help=f"Opening word for fixed-entropy (default: {FIXED_ENTROPY_OPENER})",
    )
    parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Disable Bellman pickle load/save during benchmark (not recommended)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-run every strategy even if results.json already has matching cached results",
    )
    parser.add_argument(
        "--plot-only",
        action="store_true",
        help=f"Skip running strategies; regenerate benchmark.png from {RESULTS_FILENAME}",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    if args.plot_only:
        plot_path = plot_benchmark_dir(Path(args.output_dir))
        print(f"Wrote {plot_path}")
        return 0

    table = load_pattern_table(args.dictionary, args.length)
    config = BenchmarkConfig(
        dictionary=args.dictionary,
        num_secrets=args.num_secrets,
        max_secrets=args.max_secrets,
        max_guesses=args.max_guesses,
        output_dir=args.output_dir,
        seed=args.seed,
        persist=not args.no_persist,
        fixed_opener=args.fixed_opener.lower(),
        benchmark_words_path=args.benchmark_words,
        resample_words=args.resample_words,
        force_rerun=args.force,
    )
    run_study(config, table=table, progress=True)
    plot_path = plot_benchmark_dir(config.output_dir)
    print(f"\nWrote {plot_path}")
    print(f"Wrote {results_path(config.output_dir)}")
    return 0
