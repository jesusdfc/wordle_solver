from __future__ import annotations

from solver import default_dictionary_path
from solver.agent import WordleAgent
from solver.data import PatternTable, TableLookupPersistor
from solver.env import WordleEnv
from solver.strategies import WordleStrategies

from app.schemas import ExploreResponse, HistoryRow, StrategyInfo, SuggestResponse

_table_cache: dict[int, PatternTable] = {}


def get_pattern_table(length: int = 5) -> PatternTable:
    if length not in _table_cache:
        _table_cache[length] = TableLookupPersistor(
            default_dictionary_path(),
            length=length,
        ).load(show_progress=False)
    return _table_cache[length]


def get_words(length: int = 5) -> tuple[str, ...]:
    return get_pattern_table(length).words


def get_strategies() -> list[StrategyInfo]:
    return [StrategyInfo.model_validate(item) for item in WordleStrategies.list()]


def _build_agent(
    table: PatternTable,
    strategy: str,
    *,
    opening_word: str | None = None,
) -> WordleAgent:
    return WordleAgent(
        table.words,
        strategy=strategy,
        pattern_table=table,
        dictionary_path=default_dictionary_path(),
        show_progress=False,
        opening_word=opening_word,
        belief_threshold=WordleStrategies.resolve_threshold(strategy),
    )


def _validate_opening_word(strategy: str, opening_word: str | None, words: tuple[str, ...]) -> None:
    spec = WordleStrategies.get(strategy)
    if not spec.requires_opening_word:
        return
    word = (opening_word or "").strip().lower()
    if len(word) != 5:
        raise ValueError("opening_word must be a 5-letter word for fixed-entropy")
    if word not in words:
        raise ValueError(f"{word!r} is not in the dictionary")


def suggest(
    history: list[HistoryRow],
    *,
    length: int = 5,
    max_candidates: int = 20,
    strategy: str = "entropy-threshold-bellman",
    opening_word: str | None = None,
) -> SuggestResponse:
    table = get_pattern_table(length)
    _validate_opening_word(strategy, opening_word, table.words)
    agent = _build_agent(table, strategy, opening_word=opening_word)

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


def explore(
    secret: str,
    *,
    length: int = 5,
    max_guesses: int = 6,
    strategy: str = "entropy-threshold-bellman",
    opening_word: str | None = None,
) -> ExploreResponse:
    normalized = secret.strip().lower()
    if len(normalized) != length:
        raise ValueError("5-letter word is expected")

    table = get_pattern_table(length)
    if normalized not in table.words:
        raise ValueError(f"{normalized!r} is not in the dictionary")

    _validate_opening_word(strategy, opening_word, table.words)
    agent = _build_agent(table, strategy, opening_word=opening_word)
    guesses = agent.solve(normalized, max_guesses=max_guesses)

    rows: list[HistoryRow] = []
    for guess in guesses:
        pattern = WordleEnv.pattern_to_list(table.pattern(normalized, guess), length=length)
        rows.append(HistoryRow(word=guess, pattern=pattern))

    solved = bool(guesses and guesses[-1] == normalized)
    return ExploreResponse(
        secret=normalized,
        guesses=rows,
        solved=solved,
        guess_count=len(guesses),
    )
