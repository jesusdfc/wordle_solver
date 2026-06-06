from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from solver.strategies import WordleStrategies


def _validate_strategy(value: str) -> str:
    WordleStrategies.get(value)
    return value.strip().lower()


Strategy = Annotated[str, Field(description=f"One of: {', '.join(WordleStrategies.ids())}")]


class HistoryRow(BaseModel):
    word: str = Field(min_length=1)
    pattern: list[int] = Field(min_length=5, max_length=5)


class SuggestRequest(BaseModel):
    history: list[HistoryRow] = Field(default_factory=list)
    length: int = 5
    strategy: Strategy = WordleStrategies.DEFAULT_ID
    opening_word: str | None = Field(
        default=None,
        description="Opening word for fixed-entropy (5 letters, in dictionary)",
    )

    @field_validator("strategy")
    @classmethod
    def validate_strategy(cls, value: str) -> str:
        return _validate_strategy(value)


class SuggestResponse(BaseModel):
    suggestion: str
    remaining: int
    solved: bool
    candidates: list[str] | None = None


class ExploreRequest(BaseModel):
    secret: str = Field(min_length=1)
    length: int = 5
    max_guesses: int = 6
    strategy: Strategy = WordleStrategies.DEFAULT_ID
    opening_word: str | None = None

    @field_validator("strategy")
    @classmethod
    def validate_strategy(cls, value: str) -> str:
        return _validate_strategy(value)


class ExploreResponse(BaseModel):
    secret: str
    guesses: list[HistoryRow]
    solved: bool
    guess_count: int


class StrategyInfo(BaseModel):
    id: str
    label: str
    description: str
    requires_opening_word: bool
    default_opening_word: str | None = None
    belief_threshold: int | None = None
    warning: str | None = None
