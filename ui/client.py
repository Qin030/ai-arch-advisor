"""The only UI boundary to the FastAPI service."""

from __future__ import annotations

import os
from typing import Any

import httpx


class ApiError(RuntimeError):
    """A user-presentable API failure."""


class AdvisorClient:
    def __init__(self, base_url: str | None = None, timeout: float = 15.0) -> None:
        self.base_url = (base_url or os.getenv("ADVISOR_API_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = timeout

    def start(self, utterance: str) -> dict[str, Any]:
        return self._request("POST", "/session/start", {"utterance": utterance})

    def answer(self, session_id: str, field: str, value: Any) -> dict[str, Any]:
        return self._request(
            "POST",
            "/turn",
            {"session_id": session_id, "field": field, "value": value},
        )

    def skip(self, session_id: str, field: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/turn",
            {"session_id": session_id, "field": field, "skip": True},
        )

    def summary(self, session_id: str) -> dict[str, Any]:
        return self._request("POST", "/summary", {"session_id": session_id})

    def _request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = httpx.request(
                method,
                f"{self.base_url}{path}",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as exc:
            raise ApiError("目前無法連線到服務，請確認 API 已在連接埠 8000 啟動。") from exc
        except httpx.TimeoutException as exc:
            raise ApiError("服務回應逾時，請稍後再試。") from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.json().get("detail", "服務暫時無法完成請求")
            raise ApiError(f"{detail}（HTTP {exc.response.status_code}）") from exc
        except (TypeError, ValueError) as exc:
            raise ApiError("服務回傳了無法辨識的資料格式。") from exc


client = AdvisorClient()
