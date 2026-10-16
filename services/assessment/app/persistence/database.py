"""SQLite repositories for sessions, events, assessment results, and recommendations."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any
from app.schemas.models import AssessmentResult, EventRecord, PracticeRecommendation, SessionRecord

class Repository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
              session_id TEXT PRIMARY KEY, trainee_id TEXT NOT NULL, scenario_id TEXT NOT NULL,
              scenario_version TEXT NOT NULL, rubric_id TEXT NOT NULL, rubric_version TEXT NOT NULL,
              seed INTEGER NOT NULL, status TEXT NOT NULL CHECK(status IN ('READY','RUNNING','COMPLETED','REVIEWED')),
              created_at TEXT NOT NULL, completed_at TEXT);
            CREATE INDEX IF NOT EXISTS ix_sessions_trainee_created ON sessions(trainee_id, created_at);
            CREATE TABLE IF NOT EXISTS events (
              event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
              sequence_number INTEGER NOT NULL, scenario_time_ms INTEGER NOT NULL, event_type TEXT NOT NULL,
              payload_json TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(session_id, sequence_number));
            CREATE TABLE IF NOT EXISTS assessments (
              assessment_id TEXT PRIMARY KEY, session_id TEXT NOT NULL UNIQUE REFERENCES sessions(session_id) ON DELETE CASCADE,
              scenario_id TEXT NOT NULL, scenario_version TEXT NOT NULL, rubric_id TEXT NOT NULL,
              rubric_version TEXT NOT NULL, overall_score REAL NOT NULL, result_json TEXT NOT NULL, assessed_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS recommendations (
              recommendation_id TEXT PRIMARY KEY, trainee_id TEXT NOT NULL, competency TEXT, scenario_id TEXT,
              rationale TEXT NOT NULL, evidence_assessment_ids_json TEXT NOT NULL,
              policy_version TEXT NOT NULL, created_at TEXT NOT NULL);
            """)

    @staticmethod
    def _dt(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    @classmethod
    def _session(cls, row: sqlite3.Row) -> SessionRecord:
        return SessionRecord(session_id=row["session_id"], trainee_id=row["trainee_id"], scenario_id=row["scenario_id"],
            scenario_version=row["scenario_version"], rubric_id=row["rubric_id"], rubric_version=row["rubric_version"],
            seed=row["seed"], status=row["status"], created_at=cls._dt(row["created_at"]), completed_at=cls._dt(row["completed_at"]))

    @staticmethod
    def _event(row: sqlite3.Row) -> EventRecord:
        return EventRecord(event_id=row["event_id"], session_id=row["session_id"], sequence_number=row["sequence_number"],
            scenario_time_ms=row["scenario_time_ms"], event_type=row["event_type"], payload=json.loads(row["payload_json"]),
            created_at=datetime.fromisoformat(row["created_at"]))

    def create_session(self, item: SessionRecord) -> SessionRecord:
        with self.connect() as c:
            c.execute("INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (item.session_id,item.trainee_id,item.scenario_id,item.scenario_version,item.rubric_id,item.rubric_version,
                 item.seed,item.status,item.created_at.isoformat(),item.completed_at.isoformat() if item.completed_at else None))
        return item

    def get_session(self, session_id: str) -> SessionRecord | None:
        with self.connect() as c:
            row=c.execute("SELECT * FROM sessions WHERE session_id=?",(session_id,)).fetchone()
        return self._session(row) if row else None

    def list_sessions_for_trainee(self, trainee_id: str) -> list[SessionRecord]:
        with self.connect() as c:
            rows=c.execute("SELECT * FROM sessions WHERE trainee_id=? ORDER BY created_at",(trainee_id,)).fetchall()
        return [self._session(row) for row in rows]

    def append_event(self, event: EventRecord) -> EventRecord:
        with self.connect() as c:
            session=c.execute("SELECT status FROM sessions WHERE session_id=?",(event.session_id,)).fetchone()
            if not session: raise LookupError("session_not_found")
            if session["status"] != "RUNNING": raise ValueError("session_not_running")
            previous=c.execute("SELECT sequence_number,scenario_time_ms FROM events WHERE session_id=? ORDER BY sequence_number DESC LIMIT 1",(event.session_id,)).fetchone()
            if previous:
                if event.sequence_number != previous["sequence_number"]+1: raise ValueError("event_sequence_must_increase_by_one")
                if event.scenario_time_ms < previous["scenario_time_ms"]: raise ValueError("scenario_time_must_not_decrease")
            elif event.sequence_number != 1:
                raise ValueError("first_event_sequence_must_be_one")
            c.execute("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)",(event.event_id,event.session_id,event.sequence_number,
                event.scenario_time_ms,event.event_type,json.dumps(event.payload,sort_keys=True,separators=(",",":")),event.created_at.isoformat()))
        return event

    def get_events(self, session_id: str) -> list[EventRecord]:
        with self.connect() as c:
            rows=c.execute("SELECT * FROM events WHERE session_id=? ORDER BY sequence_number",(session_id,)).fetchall()
        return [self._event(row) for row in rows]

    def complete_session(self, session_id: str, result: AssessmentResult) -> AssessmentResult:
        """Atomically transition a running session and persist its one assessment."""
        with self.connect() as c:
            row=c.execute("SELECT * FROM sessions WHERE session_id=?",(session_id,)).fetchone()
            if not row: raise LookupError("session_not_found")
            old=c.execute("SELECT result_json FROM assessments WHERE session_id=?",(session_id,)).fetchone()
            if old: return AssessmentResult.model_validate_json(old["result_json"])
            if row["status"] != "RUNNING": raise ValueError("session_not_running")
            c.execute("UPDATE sessions SET status='COMPLETED',completed_at=? WHERE session_id=?",(result.assessed_at.isoformat(),session_id))
            c.execute("INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (result.assessment_id,result.session_id,result.scenario_id,result.scenario_version,result.rubric_id,
                 result.rubric_version,result.overall_score,result.model_dump_json(),result.assessed_at.isoformat()))
        return result

    def get_assessment(self, session_id: str) -> AssessmentResult | None:
        with self.connect() as c:
            row=c.execute("SELECT result_json FROM assessments WHERE session_id=?",(session_id,)).fetchone()
        return AssessmentResult.model_validate_json(row["result_json"]) if row else None

    def list_assessments_for_trainee(self, trainee_id: str) -> list[AssessmentResult]:
        with self.connect() as c:
            rows=c.execute("SELECT a.result_json FROM assessments a JOIN sessions s ON s.session_id=a.session_id WHERE s.trainee_id=? ORDER BY a.assessed_at",(trainee_id,)).fetchall()
        return [AssessmentResult.model_validate_json(row["result_json"]) for row in rows]

    def save_recommendation(self, rec: PracticeRecommendation) -> None:
        with self.connect() as c:
            c.execute("INSERT INTO recommendations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",(rec.recommendation_id,rec.trainee_id,
                rec.competency,rec.scenario_id,rec.rationale,json.dumps(rec.evidence_assessment_ids),rec.policy_version,rec.created_at.isoformat()))

    def list_recommendations(self, trainee_id: str) -> list[PracticeRecommendation]:
        with self.connect() as c:
            rows=c.execute("SELECT * FROM recommendations WHERE trainee_id=? ORDER BY created_at DESC",(trainee_id,)).fetchall()
        return [PracticeRecommendation(recommendation_id=r["recommendation_id"],trainee_id=r["trainee_id"],
            competency=r["competency"],scenario_id=r["scenario_id"],rationale=r["rationale"],
            evidence_assessment_ids=json.loads(r["evidence_assessment_ids_json"]),policy_version=r["policy_version"],
            created_at=datetime.fromisoformat(r["created_at"])) for r in rows]

    def database_summary(self) -> dict[str, Any]:
        with self.connect() as c:
            return {table:c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    for table in ("sessions","events","assessments","recommendations")}
