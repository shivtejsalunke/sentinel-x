from __future__ import annotations
from app.adaptation.engine import recommend_practice
from app.schemas.models import AssessmentResult

def make_result(identifier: str, classification: float, decision: float = 90.0) -> AssessmentResult:
    return AssessmentResult(assessment_id=identifier, session_id=f"ses_{identifier}", scenario_id="OBS-001",
        scenario_version="1.0.0", rubric_id="RUBRIC-001", rubric_version="1.0.0-provisional",
        overall_score=classification, component_scores={"classification_accuracy":classification,
        "decision_quality":decision,"detection_and_observation":85.0,"response_time":90.0,
        "procedure_and_reporting":100.0,"confidence_calibration":88.0}, metrics={})

def test_recommendation_targets_repeated_low_competency() -> None:
    scenarios={"OBS-001":{"learning_objectives":["classification_accuracy"],"difficulty_band":"beginner"},
               "OBS-002":{"learning_objectives":["uncertainty_reporting"],"difficulty_band":"intermediate"}}
    rec=recommend_practice("trainee_demo",[make_result("one",50),make_result("two",55)],scenarios)
    assert rec.competency=="classification_accuracy"
    assert rec.scenario_id=="OBS-001"
    assert "repeated weakness" in rec.rationale

def test_no_history_recommends_baseline() -> None:
    rec=recommend_practice("trainee_demo",[],{})
    assert rec.scenario_id is None
    assert "baseline" in rec.rationale
