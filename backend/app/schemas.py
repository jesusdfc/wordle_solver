from pydantic import BaseModel, Field


class HistoryRow(BaseModel):
    word: str = Field(min_length=1)
    pattern: list[int] = Field(min_length=5, max_length=5)


class SuggestRequest(BaseModel):
    history: list[HistoryRow] = Field(default_factory=list)
    length: int = 5


class SuggestResponse(BaseModel):
    suggestion: str
    remaining: int
    solved: bool
    candidates: list[str] | None = None


class BenchmarkRequest(BaseModel):
    secret: str = Field(min_length=1)
    length: int = 5
    max_guesses: int = 6


class BenchmarkResponse(BaseModel):
    secret: str
    guesses: list[HistoryRow]
    solved: bool
    guess_count: int
