"""FastAPI entry point.

Day 1 scope: /health only. Every other endpoint returns 501 until D2, when they
start serving the fixtures in schema/examples/. See docs/CONTRACT.md.
"""

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="AI 建築前期決策助理",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "kb_slices": 0,
        "region_allowlist": settings.region_allowlist,
    }
