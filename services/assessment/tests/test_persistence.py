from __future__ import annotations
from pathlib import Path
from app.persistence.database import Repository
from app.schemas.models import SessionRecord

def test_session_persists_after_repository_reopen(tmp_path: Path) -> None:
    path=tmp_path/"records.sqlite3"; first=Repository(path)
    session=SessionRecord(session_id="ses_persist",trainee_id="trainee_persist",scenario_id="OBS-001",
        scenario_version="1.0.0",rubric_id="RUBRIC-001",rubric_version="1.0.0-provisional",seed=42)
    first.create_session(session); restored=Repository(path).get_session("ses_persist")
    assert restored is not None
    assert restored.trainee_id=="trainee_persist"
    assert restored.seed==42
