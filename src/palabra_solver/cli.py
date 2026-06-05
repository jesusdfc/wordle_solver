"""Command-line interface for the Wordle solver."""

from __future__ import annotations

import argparse
from pathlib import Path

from palabra_solver.feedback import pattern, pattern_to_str
from palabra_solver.model import Solver, Strategy
from palabra_solver.words import WordleWordsHandler

DEFAULT_LEMARIO = Path(__file__).resolve().parents[2] / "lemario-general-del-espanol.txt"


def _load_words(path: Path, length: int) -> tuple[str, ...]:
    return WordleWordsHandler(path, length=length).load().words


def cmd_stats(args: argparse.Namespace) -> int:
    words = _load_words(args.dictionary, args.length)
    print(f"Dictionary: {args.dictionary}")
    print(f"Length: {args.length}")
    print(f"Valid words: {len(words)}")
    if words:
        print(f"Sample: {', '.join(words[:10])}")
    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    words = _load_words(args.dictionary, args.length)
    solver = Solver(words, strategy=Strategy(args.strategy))

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
        solver.update(guess, feedback_pattern)

    suggestion = solver.suggest()
    remaining = len(solver.candidates)
    print(f"Suggested guess: {suggestion}")
    print(f"Remaining candidates: {remaining}")
    if remaining <= args.show:
        print("Candidates:", ", ".join(solver.candidates))
    return 0


def cmd_solve(args: argparse.Namespace) -> int:
    words = _load_words(args.dictionary, args.length)
    solver = Solver(words, strategy=Strategy(args.strategy))
    guesses = solver.solve(args.secret.lower(), max_guesses=args.max_guesses)

    print(f"Secret: {args.secret.lower()}")
    for index, guess in enumerate(guesses, start=1):
        feedback = pattern_to_str(
            pattern(args.secret.lower(), guess),
            length=args.length,
            use_emoji=False,
        )
        print(f"  {index}. {guess}  {feedback}")

    solved = guesses and guesses[-1] == args.secret.lower()
    print(f"Solved in {len(guesses)} guesses" if solved else "Not solved")
    return 0 if solved else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optimal solver for La Palabra del Día")
    parser.add_argument(
        "--dictionary",
        type=Path,
        default=DEFAULT_LEMARIO,
        help="Path to the Spanish dictionary file",
    )
    parser.add_argument("--length", type=int, default=5, help="Word length (default: 5)")

    subparsers = parser.add_subparsers(dest="command", required=True)

    stats = subparsers.add_parser("stats", help="Show dictionary statistics")
    stats.set_defaults(func=cmd_stats)

    suggest = subparsers.add_parser("suggest", help="Suggest the next optimal guess")
    suggest.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in Strategy],
        default=Strategy.ENTROPY.value,
    )
    suggest.add_argument(
        "--guess",
        action="append",
        default=[],
        metavar="WORD+PATTERN",
        help="Previous guess and base-3 pattern, e.g. audio02201",
    )
    suggest.add_argument(
        "--show",
        type=int,
        default=20,
        help="Show remaining candidates when count is at most this value",
    )
    suggest.set_defaults(func=cmd_suggest)

    solve = subparsers.add_parser("solve", help="Simulate solving a known secret offline")
    solve.add_argument("secret", help="Secret word to solve")
    solve.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in Strategy],
        default=Strategy.ENTROPY.value,
    )
    solve.add_argument("--max-guesses", type=int, default=6)
    solve.set_defaults(func=cmd_solve)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
