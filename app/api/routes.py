"""HTTP layer. Validates input, delegates, returns. No business logic here.

D2: all three endpoints delegate to app.core.fixtures for fixed fake data.
See docs/CONTRACT.md 分階段實作.
"""

from fastapi import APIRouter, HTTPException

from app.core import fixtures
from app.core.models import StartRequest, SummaryRequest, TurnRequest

router = APIRouter()

_UNKNOWN_SESSION = "session_id 不存在或已過期"


@router.post("/session/start")
def start_session(req: StartRequest) -> dict:
    return fixtures.start_session(req.utterance).model_dump()


@router.post("/turn")
def take_turn(req: TurnRequest) -> dict:
    try:
        return fixtures.take_turn(req.session_id).model_dump()
    except KeyError as err:
        raise HTTPException(status_code=404, detail=_UNKNOWN_SESSION) from err


@router.post("/summary")
def build_summary(req: SummaryRequest) -> dict:
    try:
        return fixtures.build_summary(req.session_id).model_dump()
    except KeyError as err:
        raise HTTPException(status_code=404, detail=_UNKNOWN_SESSION) from err
