"""Explore a secret: run the solver and print the guess path."""

from __future__ import annotations

import argparse

from solver.cli.helpers import build_agent, load_pattern_table
from solver.env import WordleEnv


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "explore",
        help="Simulate solving a known secret and show the guess path",
        description=(
            "Mirror of the Explore tab in the web app. Given a secret word, "
            "runs the full guess loop (up to six attempts) and prints each guess "
            "with ASCII feedback (. gray, y yellow, g green)."
        ),
    )
    parser.add_argument("secret", help="Secret word to solve (must be in the dictionary)")
    parser.add_argument(
        "--max-guesses",
        type=int,
        default=6,
        help="Maximum number of guesses before giving up (default: 6)",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    table = load_pattern_table(args.dictionary, args.length)
    agent = build_agent(
        table,
        args.strategy,
        args.dictionary,
        opening_word=args.opening_word,
        show_progress=False,
    )
    guesses = agent.solve(args.secret.lower(), max_guesses=args.max_guesses)

    print(f"Secret: {args.secret.lower()}")
    for index, guess in enumerate(guesses, start=1):
        feedback = WordleEnv.pattern_to_str(
            table.pattern(args.secret.lower(), guess),
            length=args.length,
            use_emoji=False,
        )
        print(f"  {index}. {guess}  {feedback}")

    solved = guesses and guesses[-1] == args.secret.lower()
    print(f"Solved in {len(guesses)} guesses" if solved else "Not solved")
    return 0 if solved else 1
