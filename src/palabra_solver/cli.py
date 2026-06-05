"""Command-line interface for the Wordle solver."""

from __future__ import annotations

import argparse
from pathlib import Path

from palabra_solver.agent import Strategy, WordleAgent
from palabra_solver.data import WordleWordsHandler
from palabra_solver.env import WordleEnv

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
    agent = WordleAgent(words, strategy=Strategy(args.strategy))

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


def cmd_solve(args: argparse.Namespace) -> int:
    words = _load_words(args.dictionary, args.length)
    agent = WordleAgent(words, strategy=Strategy(args.strategy))
    guesses = agent.solve(args.secret.lower(), max_guesses=args.max_guesses)

    print(f"Secret: {args.secret.lower()}")
    for index, guess in enumerate(guesses, start=1):
        feedback = WordleEnv.pattern_to_str(
            WordleEnv.pattern(args.secret.lower(), guess),
            length=args.length,
            use_emoji=False,
        )
        print(f"  {index}. {guess}  {feedback}")

    solved = guesses and guesses[-1] == args.secret.lower()
    print(f"Solved in {len(guesses)} guesses" if solved else "Not solved")
    return 0 if solved else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Optimal solver for La Palabra del Día (Spanish Wordle).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
                commands:
                stats     Inspect the loaded dictionary (word count, sample entries).
                suggest   Pick the best next guess from your in-game feedback so far.
                solve     Run the solver offline against a known secret for testing.
                """.strip(),
    )
    parser.add_argument(
        "--dictionary",
        type=Path,
        default=DEFAULT_LEMARIO,
        help="Path to the Spanish dictionary file (default: lemario at project root)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=5,
        help="Word length to filter for (default: 5, classic mode)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    stats = subparsers.add_parser(
        "stats",
        help="Show dictionary statistics",
        description=(
            "Load the dictionary, apply Wordle normalization (strip accents, drop "
            "hyphens/spaces, keep ñ), and print how many playable words remain."
        ),
    )
    stats.set_defaults(func=cmd_stats)

    suggest = subparsers.add_parser(
        "suggest",
        help="Suggest the next optimal guess",
        description=(
            "Interactive assistant for an in-progress game. Pass each previous guess "
            "with its color pattern; the solver filters possible secrets and returns "
            "the guess that maximizes information (entropy or minimax).\n\n"
            "Pattern digits are base-3 per position: 0=gray, 1=yellow, 2=green. "
            "Example for a 5-letter word: audio02201 means audio with g g . y ."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    suggest.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in Strategy],
        default=Strategy.ENTROPY.value,
        help="entropy: maximize expected information; minimax: minimize worst-case bucket size",
    )
    suggest.add_argument(
        "--guess",
        action="append",
        default=[],
        metavar="WORD+PATTERN",
        help="Previous guess plus base-3 pattern, e.g. audio02201 (repeat for each row played)",
    )
    suggest.add_argument(
        "--show",
        type=int,
        default=20,
        help="List remaining candidate secrets when the count is at most this value",
    )
    suggest.set_defaults(func=cmd_suggest)

    solve = subparsers.add_parser(
        "solve",
        help="Simulate solving a known secret offline",
        description=(
            "Benchmark the solver without playing manually. Given a secret word, "
            "runs the full guess loop (up to six attempts) and prints each guess "
            "with ASCII feedback (. gray, y yellow, g green)."
        ),
    )
    solve.add_argument("secret", help="Secret word to solve (must be in the dictionary)")
    solve.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in Strategy],
        default=Strategy.ENTROPY.value,
        help="entropy: maximize expected information; minimax: minimize worst-case bucket size",
    )
    solve.add_argument(
        "--max-guesses",
        type=int,
        default=6,
        help="Maximum number of guesses before giving up (default: 6)",
    )
    solve.set_defaults(func=cmd_solve)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
