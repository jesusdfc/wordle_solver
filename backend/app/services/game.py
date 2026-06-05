from __future__ import annotations

from solver import default_dictionary_path
from solver.agent import WordleAgent
from solver.data import PatternTable, TableLookupPersistor
from solver.env import WordleEnv
from solver.model import WordleModel

from app.schemas import BenchmarkResponse, HistoryRow, SuggestResponse

_table_cache: dict[int, PatternTable] = {}


def get_pattern_table(length: int = 5) -> PatternTable:
    if length not in _table_cache:
        _table_cache[length] = TableLookupPersistor(
            default_dictionary_path(),
            length=length,
        ).load()
    return _table_cache[length]


def get_words(length: int = 5) -> tuple[str, ...]:
    return get_pattern_table(length).words


def suggest(
    history: list[HistoryRow],
    *,
    length: int = 5,
    max_candidates: int = 20,
) -> SuggestResponse:
    table = get_pattern_table(length)
    model = WordleModel(pattern_table=table)
    agent = WordleAgent(table.words, model=model, pattern_table=table)

    for row in history:
        if len(row.word) != length or len(row.pattern) != length:
            raise ValueError(f"Each row must have {length} letters and {length} pattern codes")
        for code in row.pattern:
            if code not in (0, 1, 2):
                raise ValueError("Pattern codes must be 0 (gray), 1 (yellow), or 2 (green)")

        pattern = WordleEnv.pattern_from_list(row.pattern)
        agent.update(row.word.lower(), pattern)

    remaining = len(agent.candidates)
    return SuggestResponse(
        suggestion=agent.suggest(),
        remaining=remaining,
        solved=agent.belief.is_solved(),
        candidates=list(agent.candidates) if remaining <= max_candidates else None,
    )


def benchmark(
    secret: str,
    *,
    length: int = 5,
    max_guesses: int = 6,
) -> BenchmarkResponse:
    normalized = secret.strip().lower()
    if len(normalized) != length:
        raise ValueError("5-letter word is expected")

    table = get_pattern_table(length)
    if normalized not in table.words:
        raise ValueError(f"{normalized!r} is not in the dictionary")

    agent = WordleAgent(table.words, model=WordleModel(pattern_table=table), pattern_table=table)
    guesses = agent.solve(normalized, max_guesses=max_guesses)

    rows: list[HistoryRow] = []
    for guess in guesses:
        pattern = WordleEnv.pattern_to_list(table.pattern(normalized, guess), length=length)
        rows.append(HistoryRow(word=guess, pattern=pattern))

    solved = bool(guesses and guesses[-1] == normalized)
    return BenchmarkResponse(
        secret=normalized,
        guesses=rows,
        solved=solved,
        guess_count=len(guesses),
    )
