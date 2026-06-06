"""Interactive play: suggest next guess from in-game feedback."""

from __future__ import annotations

import argparse

from solver.cli.helpers import build_agent, load_pattern_table


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "play",
        help="Suggest the next optimal guess (interactive assistant)",
        description=(
            "Mirror of the Play screen in the web app. Pass each previous guess "
            "with its color pattern; the solver filters possible secrets and returns "
            "the next suggestion.\n\n"
            "Pattern digits are base-3 per position: 0=gray, 1=yellow, 2=green. "
            "Example for a 5-letter word: audio02201 means audio with g g . y ."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--guess",
        action="append",
        default=[],
        metavar="WORD+PATTERN",
        help="Previous guess plus base-3 pattern, e.g. audio02201 (repeat for each row played)",
    )
    parser.add_argument(
        "--show",
        type=int,
        default=20,
        help="List remaining candidate secrets when the count is at most this value",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    table = load_pattern_table(args.dictionary, args.length)
    agent = build_agent(
        table,
        args.strategy,
        args.dictionary,
        opening_word=args.opening_word,
    )

    for guess_feedback in args.guess:
        if len(guess_feedback) != args.length + 1:
            raise SystemExit(
                f"Each --guess must be WORD+PATTERN, e.g. audio02201 for length {args.length}"
            )
        guess = guess_feedback[: args.length].lower()
        pattern_str = guess_feedback[args.length :]
        if not pattern_str.isdigit():
            raise SystemExit("Pattern must be digits 0=gray, 1=yellow, 2=green")

        feedback_pattern = 0
        for index, digit in enumerate(pattern_str):
            feedback_pattern += int(digit) * (3**index)
        agent.update(guess, feedback_pattern)

    suggestion = agent.suggest()
    remaining = len(agent.candidates)
    print(f"Suggested guess: {suggestion}")
    print(f"Remaining candidates: {remaining}")
    if remaining <= args.show:
        print("Candidates:", ", ".join(agent.candidates))
    return 0
