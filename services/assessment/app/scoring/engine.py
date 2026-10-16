"""Deterministic assessment calculations over structured event evidence."""
from __future__ import annotations
from collections.abc import Mapping, Sequence
from typing import Any
from app.schemas.models import AssessmentResult, EventRecord, MetricValue, SessionRecord

# Prototype weights only. A qualified training authority must approve the rubric before formal use.
RUBRIC_ID = "RUBRIC-001"
RUBRIC_VERSION = "1.0.0-provisional"
WEIGHTS: dict[str, float] = {
    "classification_accuracy": 0.25,
    "decision_quality": 0.25,
    "detection_and_observation": 0.20,
    "response_time": 0.10,
    "procedure_and_reporting": 0.10,
    "confidence_calibration": 0.10,
}

def _metric(value: float | None, numerator: float | None, denominator: float | None) -> MetricValue:
    return MetricValue(value=value, numerator=numerator, denominator=denominator, unit="ratio",
                       status="available" if value is not None else "not_available")

def score_session(session: SessionRecord, events: Sequence[EventRecord],
                  ground_truth: Mapping[str, Any]) -> AssessmentResult:
    """Score recorded decisions against synthetic ground truth using deterministic rules."""
    expected = ground_truth.get("observations", {})
    evaluated = correct = false_positive = false_negative = confidence_count = 0
    confidence_error = 0.0
    response_times: list[int] = []
    errors: list[str] = []
    flags: list[str] = []
    event_ids: list[str] = []
    for event in sorted(events, key=lambda item: item.sequence_number):
        payload = event.payload
        observation_id = str(payload.get("observation_id", ""))
        label = expected.get(observation_id)
        if not isinstance(label, dict):
            errors.append("unknown_observation")
            flags.append(f"event:{event.event_id}:missing_ground_truth")
            continue
        submitted = str(payload.get("response_category", ""))
        is_correct = submitted == str(label.get("expected_category", ""))
        evaluated += 1
        correct += int(is_correct)
        confidence = float(payload.get("confidence", 0.5))
        confidence_error += (confidence - float(is_correct)) ** 2
        confidence_count += 1
        response_times.append(event.scenario_time_ms)
        event_ids.append(event.event_id)
        if not is_correct:
            errors.append("classification_error")
            flags.append(f"event:{event.event_id}:classification_mismatch")
        if bool(label.get("is_relevant", False)) and submitted == "no_observation":
            false_negative += 1
            errors.append("missed_observation")
        if not bool(label.get("is_relevant", False)) and submitted != "no_observation":
            false_positive += 1
            errors.append("false_positive")
    accuracy = correct / evaluated if evaluated else None
    non_relevant = sum(1 for item in expected.values() if isinstance(item, dict) and not item.get("is_relevant", False))
    relevant = sum(1 for item in expected.values() if isinstance(item, dict) and item.get("is_relevant", False))
    fp_rate = false_positive / non_relevant if non_relevant else None
    miss_rate = false_negative / relevant if relevant else None
    mean_latency = sum(response_times) / len(response_times) if response_times else None
    brier = confidence_error / confidence_count if confidence_count else None
    def percent(value: float | None) -> float:
        return round(value * 100, 4) if value is not None else 0.0
    components = {
        "classification_accuracy": percent(accuracy),
        "decision_quality": percent(accuracy),
        "detection_and_observation": percent(accuracy),
        "response_time": 100.0 if mean_latency is not None and mean_latency <= 15000 else 50.0,
        "procedure_and_reporting": 100.0,
        "confidence_calibration": percent(1.0 - brier if brier is not None else None),
    }
    overall = round(sum(WEIGHTS[key] * components[key] for key in WEIGHTS), 4)
    metrics = {
        "classification_accuracy": _metric(accuracy, float(correct), float(evaluated)),
        "false_positive_rate": _metric(fp_rate, float(false_positive), float(non_relevant)),
        "miss_rate": _metric(miss_rate, float(false_negative), float(relevant)),
        "mean_response_time_ms": MetricValue(value=round(mean_latency, 3) if mean_latency is not None else None,
            numerator=round(sum(response_times), 3) if response_times else None,
            denominator=float(len(response_times)) if response_times else None, unit="milliseconds",
            status="available" if mean_latency is not None else "not_available"),
        "confidence_brier_score": MetricValue(value=round(brier, 6) if brier is not None else None,
            numerator=round(confidence_error, 6) if confidence_count else None,
            denominator=float(confidence_count) if confidence_count else None,
            unit="squared_probability_error", status="available" if brier is not None else "not_available"),
    }
    if not evaluated:
        flags.append("no_evaluated_observations")
    return AssessmentResult(session_id=session.session_id, scenario_id=session.scenario_id,
        scenario_version=session.scenario_version, rubric_id=session.rubric_id,
        rubric_version=session.rubric_version, overall_score=overall, component_scores=components,
        metrics=metrics, error_categories=sorted(set(errors)), critical_flags=sorted(set(flags)),
        event_ids=event_ids)
