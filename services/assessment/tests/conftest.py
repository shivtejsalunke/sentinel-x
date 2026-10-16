from __future__ import annotations
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

@pytest.fixture()
def service_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SENTINEL_X_DATABASE_PATH", str(tmp_path / "test.sqlite3"))
    monkeypatch.setenv("SENTINEL_X_SCENARIO_DIR", str(Path(__file__).resolve().parents[3] / "scenarios" / "approved"))
    from app.main import app
    app.state.repository = None
    app.state.scenarios = None
    with TestClient(app) as client:
        yield client
