from __future__ import annotations
from app.schemas.models import EventRecord, SessionRecord
from app.scoring.engine import score_session

def make_session() -> SessionRecord:
    return SessionRecord(session_id="ses_test", trainee_id="trainee_test", scenario_id="OBS-001",
        scenario_version="1.0.0", rubric_id="RUBRIC-001", rubric_version="1.0.0-provisional", seed=1)

def make_event(sequence: int, observation_id: str, category: str, confidence: float = 0.8) -> EventRecord:
    return EventRecord(event_id=f"evt_{sequence}", session_id="ses_test", sequence_number=sequence,
        scenario_time_ms=sequence*1000, event_type="classification_submitted",
        payload={"observation_id": observation_id, "response_category": category, "confidence": confidence})

def test_score_is_deterministic_for_same_evidence() -> None:
    session = make_session()
    events = [make_event(1,"obs-001","category_a",0.8), make_event(2,"obs-002","category_c",0.9), make_event(3,"obs-003","no_observation",0.7)]
    truth = {"observations": {"obs-001":{"expected_category":"category_a","is_relevant":True},
        "obs-002":{"expected_category":"category_b","is_relevant":True},
        "obs-003":{"expected_category":"no_observation","is_relevant":False}}}
    first = score_session(session,events,truth); second = score_session(session,events,truth)
    assert first.overall_score == second.overall_score
    assert first.component_scores == second.component_scores
    assert first.error_categories == second.error_categories
    assert first.event_ids == second.event_ids

def test_no_events_does_not_claim_metric_availability() -> None:
    result = score_session(make_session(), [], {"observations": {}})
    assert result.metrics["classification_accuracy"].value is None
    assert result.metrics["classification_accuracy"].status == "not_available"
    assert "no_evaluated_observations" in result.critical_flags

def test_scoring_records_mismatch_evidence() -> None:
    session=make_session(); event=make_event(1,"obs-001","category_c")
    result=score_session(session,[event],{"observations":{"obs-001":{"expected_category":"category_a","is_relevant":True}}})
    assert "classification_error" in result.error_categories
    assert f"event:{event.event_id}:classification_mismatch" in result.critical_flags
    assert event.event_id in result.event_ids
