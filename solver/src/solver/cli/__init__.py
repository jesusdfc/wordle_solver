"""Command-line interface for the Wordle solver."""

from __future__ import annotations

import argparse

from solver.cli import benchmark, explore, play
from solver.cli.helpers import add_global_arguments, load_pattern_table
from solver.model.threshold_bellman import ThresholdBellmanModel


def cmd_stats(args: argparse.Namespace) -> int:
    table = load_pattern_table(args.dictionary, args.length)
    words = table.words
    print(f"Dictionary: {args.dictionary}")
    print(f"Length: {args.length}")
    print(f"Valid words: {len(words)}")
    if words:
        print(f"Sample: {', '.join(words[:10])}")
    return 0


def cmd_warm_bellman_cache(args: argparse.Namespace) -> int:
    table = load_pattern_table(args.dictionary, args.length)
    words = table.words
    if args.dictionary_size > 0:
        words = words[: args.dictionary_size]

    model = ThresholdBellmanModel(
        words,
        pattern_table=table,
        dictionary_path=args.dictionary,
        length=args.length,
        show_progress=True,
    )
    solved = model.warm_cache(words, max_beliefs=args.max_beliefs or None)
    print(f"Dictionary words: {len(words)}")
    print(f"Newly solved beliefs: {solved}")
    print(f"Total cached beliefs: {model.cached_beliefs}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Optimal solver for La Palabra del Día (Spanish Wordle).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
                commands:
                play                Interactive suggestions (web Play tab).
                explore             Solve a known secret and show the path (web Explore tab).
                benchmark           Compare all strategies and export plots.
                stats               Dictionary statistics.
                warm-bellman-cache  Precompute Bellman value-function cache.
                """.strip(),
    )
    add_global_arguments(parser)

    subparsers = parser.add_subparsers(dest="command", required=True)

    play.register(subparsers)
    explore.register(subparsers)
    benchmark.register(subparsers)

    stats = subparsers.add_parser("stats", help="Show dictionary statistics")
    stats.set_defaults(func=cmd_stats)

    warm = subparsers.add_parser(
        "warm-bellman-cache",
        help="Precompute Bellman value-function cache bottom-up",
    )
    warm.add_argument(
        "--dictionary-size",
        type=int,
        default=0,
        help="Use only the first N dictionary words (0 = full dictionary, default)",
    )
    warm.add_argument(
        "--max-beliefs",
        type=int,
        default=0,
        help="Stop after discovering this many beliefs (0 = no limit, default)",
    )
    warm.set_defaults(func=cmd_warm_bellman_cache)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
