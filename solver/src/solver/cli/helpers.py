"""Shared CLI helpers."""

from __future__ import annotations

import argparse
from pathlib import Path

from solver import default_dictionary_path
from solver.agent import WordleAgent
from solver.data import TableLookupPersistor
from solver.strategies import WordleStrategies


def load_pattern_table(path: Path, length: int):
    return TableLookupPersistor(path, length=length).load()


def build_agent(
    table,
    strategy: str,
    dictionary: Path,
    *,
    opening_word: str | None = None,
    show_progress: bool = True,
) -> WordleAgent:
    return WordleAgent(
        table.words,
        strategy=strategy,
        pattern_table=table,
        dictionary_path=dictionary,
        show_progress=show_progress,
        opening_word=opening_word,
    )


def add_global_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--strategy",
        choices=WordleStrategies.ids(),
        default=WordleStrategies.DEFAULT_ID,
        help="Solver strategy (see: GET /api/strategies)",
    )
    parser.add_argument(
        "--dictionary",
        type=Path,
        default=default_dictionary_path(),
        help="Path to the Spanish dictionary file (default: data/lemario at repo root)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=5,
        help="Word length to filter for (default: 5, classic mode)",
    )
    parser.add_argument(
        "--opening-word",
        default=None,
        help="Opening word for fixed-entropy (default: cario)",
    )
