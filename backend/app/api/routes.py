from fastapi import APIRouter, HTTPException

from app.schemas import BenchmarkRequest, BenchmarkResponse, SuggestRequest, SuggestResponse
from app.services.game import benchmark, suggest

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/suggest", response_model=SuggestResponse)
def suggest_next(request: SuggestRequest) -> SuggestResponse:
    try:
        return suggest(
            request.history,
            length=request.length,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/benchmark", response_model=BenchmarkResponse)
def run_benchmark(request: BenchmarkRequest) -> BenchmarkResponse:
    try:
        return benchmark(
            request.secret,
            length=request.length,
            max_guesses=request.max_guesses,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
