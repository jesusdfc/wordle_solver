from fastapi import APIRouter, HTTPException

from app.schemas import SuggestRequest, SuggestResponse
from app.services.game import suggest

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/suggest", response_model=SuggestResponse)
def suggest_next(request: SuggestRequest) -> SuggestResponse:
    try:
        return suggest(
            request.history,
            strategy=request.strategy,
            length=request.length,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
