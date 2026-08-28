"""HTTP layer. Validates input, delegates, returns. No business logic here.

Day 1: all three endpoints return 501. D2 replaces the bodies with fixtures
from schema/examples/ so the UI can be built against a stable shape.
"""

from fastapi import APIRouter, HTTPException

from app.core.models import StartRequest, SummaryRequest, TurnRequest

router = APIRouter()

_NOT_YET = "尚未實作，預計 D2 提供假資料版本。見 docs/CONTRACT.md 的分階段實作表。"


@router.post("/session/start")
def start_session(req: StartRequest) -> dict:
    raise HTTPException(status_code=501, detail=_NOT_YET)


@router.post("/turn")
def take_turn(req: TurnRequest) -> dict:
    raise HTTPException(status_code=501, detail=_NOT_YET)


@router.post("/summary")
def build_summary(req: SummaryRequest) -> dict:
    raise HTTPException(status_code=501, detail=_NOT_YET)
