from __future__ import annotations

from solver import default_dictionary_path
from solver.agent import WordleAgent
from solver.data import WordleWordsHandler
from solver.env import WordleEnv
from solver.model import Strategy, WordleModel

from app.schemas import HistoryRow, SuggestResponse

_words_cache: dict[int, tuple[str, ...]] = {}


def get_words(length: int = 5) -> tuple[str, ...]:
    if length not in _words_cache:
        _words_cache[length] = WordleWordsHandler(
            default_dictionary_path(),
            length=length,
        ).load().words
    return _words_cache[length]


def suggest(
    history: list[HistoryRow],
    *,
    strategy: str = "entropy",
    length: int = 5,
    max_candidates: int = 20,
) -> SuggestResponse:
    words = get_words(length)
    model = WordleModel(strategy=Strategy(strategy))
    agent = WordleAgent(words, model=model)

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
