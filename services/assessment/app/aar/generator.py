"""Generate a compact AAR from saved assessment fields and recorded events."""
from __future__ import annotations
from typing import Any
from app.schemas.models import AssessmentResult, EventRecord, SessionRecord

def generate_aar(session: SessionRecord, assessment: AssessmentResult,
                 events: list[EventRecord]) -> dict[str, Any]:
    event_by_id = {event.event_id: event for event in events}
    timeline = [{"event_id": event.event_id, "sequence_number": event.sequence_number,
                 "scenario_time_ms": event.scenario_time_ms, "event_type": event.event_type,
                 "payload": event.payload} for event in events]
    flags = []
    for flag in assessment.critical_flags:
        event_id = flag.split(":", 2)[1] if flag.startswith("event:") else None
        flags.append({"flag": flag, "event_id": event_id if event_id in event_by_id else None,
                      "evidence_available": bool(event_id and event_id in event_by_id)})
    return {"session_id": session.session_id, "trainee_id": session.trainee_id,
        "scenario_id": session.scenario_id, "scenario_version": session.scenario_version,
        "rubric_id": assessment.rubric_id, "rubric_version": assessment.rubric_version,
        "overall_score": assessment.overall_score, "component_scores": assessment.component_scores,
        "metrics": {key: value.model_dump(mode="json") for key,value in assessment.metrics.items()},
        "error_categories": assessment.error_categories, "review_flags": flags, "timeline": timeline,
        "interpretation": "This report summarizes only persisted synthetic session evidence. Component weights and training rules are provisional until reviewed by qualified training personnel."}
