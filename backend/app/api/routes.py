from fastapi import APIRouter, HTTPException

from app.schemas import ExploreRequest, ExploreResponse, StrategyInfo, SuggestRequest, SuggestResponse
from app.services.game import explore, get_strategies, suggest

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/strategies", response_model=list[StrategyInfo])
def list_solver_strategies() -> list[StrategyInfo]:
    return get_strategies()


@router.post("/suggest", response_model=SuggestResponse)
def suggest_next(request: SuggestRequest) -> SuggestResponse:
    try:
        return suggest(
            request.history,
            length=request.length,
            strategy=request.strategy,
            opening_word=request.opening_word,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/explore", response_model=ExploreResponse)
def run_explore(request: ExploreRequest) -> ExploreResponse:
    try:
        return explore(
            request.secret,
            length=request.length,
            max_guesses=request.max_guesses,
            strategy=request.strategy,
            opening_word=request.opening_word,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
