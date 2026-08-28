import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def schema():
    return json.loads((ROOT / "schema" / "requirement.schema.json").read_text("utf-8"))


@pytest.fixture
def example():
    """Load a fixture from schema/examples/ by name: example("complete")."""

    def _load(name: str):
        return json.loads((ROOT / "schema" / "examples" / f"{name}.json").read_text("utf-8"))

    return _load
