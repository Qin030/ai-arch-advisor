"""HTTP layer. Validates input, delegates, returns. No business logic here.

D3: /session/start and /turn run the real decision tree in
app.core.question_tree. /summary still serves the D2 fixture — D6 replaces it.
See docs/CONTRACT.md 分階段實作.
"""

from fastapi import APIRouter, HTTPException

from app.core import fixtures, question_tree
from app.core.models import StartRequest, SummaryRequest, TurnRequest

router = APIRouter()

_UNKNOWN_SESSION = "session_id 不存在或已過期"


@router.post("/session/start")
def start_session(req: StartRequest) -> dict:
    return question_tree.start_session(req.utterance).model_dump()


@router.post("/turn")
def take_turn(req: TurnRequest) -> dict:
    try:
        return question_tree.take_turn(req.session_id, value=req.value, skip=req.skip).model_dump()
    except question_tree.UnknownSession as err:
        raise HTTPException(status_code=404, detail=_UNKNOWN_SESSION) from err
    except question_tree.InvalidAnswer as err:
        # Same code as a body that fails pydantic (see app/main.py): one kind of
        # failure, one status. docs/CONTRACT.md 〈錯誤〉 has no second code for it.
        raise HTTPException(status_code=400, detail=str(err)) from err


@router.post("/summary")
def build_summary(req: SummaryRequest) -> dict:
    if not question_tree.has_session(req.session_id):
        raise HTTPException(status_code=404, detail=_UNKNOWN_SESSION)
    return fixtures.build_summary(req.session_id).model_dump()
