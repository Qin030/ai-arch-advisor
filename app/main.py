"""FastAPI entry point.

Day 1 scope: /health only. Every other endpoint returns 501 until D2, when they
start serving the fixtures in schema/examples/. See docs/CONTRACT.md.
"""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="AI 建築前期決策助理",
    version="0.1.0",
)


@app.exception_handler(RequestValidationError)
async def _request_validation_returns_400(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """FastAPI answers a malformed body with 422; the contract says 400.

    docs/CONTRACT.md 〈錯誤〉 lists exactly one code for a request that does not
    match the schema, and it is 400. 422 is FastAPI's default, not a decision
    this project made, and letting it through would give the same failure two
    codes depending on which layer caught it.

    This runs before any route body, so a rejected request never reaches
    fixtures.take_turn — a malformed turn cannot consume a group. That is
    docs/specs/translation-tree.md 二 step 3: a type error is not a "processed"
    turn, progress does not move, the client resends the same group.
    """
    return JSONResponse(status_code=400, content={"detail": jsonable_encoder(exc.errors())})


app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "kb_slices": 0,
        "region_allowlist": settings.region_allowlist,
    }
