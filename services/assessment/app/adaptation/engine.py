"""Transparent rules for selecting targeted follow-up practice."""
from __future__ import annotations
from collections.abc import Sequence
from typing import Any
from app.schemas.models import AssessmentResult, PracticeRecommendation

COMPETENCY_TO_SCENARIO_TAG = {
    "classification_accuracy": "classification_accuracy",
    "decision_quality": "decision_quality",
    "detection_and_observation": "observation_quality",
    "response_time": "response_timing",
    "procedure_and_reporting": "reporting_completeness",
    "confidence_calibration": "uncertainty_reporting",
}

def recommend_practice(trainee_id: str, assessments: Sequence[AssessmentResult],
                       scenarios: dict[str, dict[str, Any]]) -> PracticeRecommendation:
    """Recommend practice when recent assessment evidence supports a competency gap."""
    if not assessments:
        return PracticeRecommendation(trainee_id=trainee_id, competency=None, scenario_id=None,
            rationale="No completed assessment evidence is available; complete a baseline exercise first.")
    recent = list(assessments[-3:])
    names = sorted({key for item in recent for key in item.component_scores})
    means = {name: sum(item.component_scores[name] for item in recent if name in item.component_scores)
             / sum(1 for item in recent if name in item.component_scores)
             for name in names if any(name in item.component_scores for item in recent)}
    weakest = min(means, key=means.get) if means else None
    if weakest is None:
        return PracticeRecommendation(trainee_id=trainee_id, competency=None, scenario_id=None,
            rationale="The available assessment evidence does not include competency component scores.",
            evidence_assessment_ids=[item.assessment_id for item in recent])
    supporting = [item for item in recent if weakest in item.component_scores and item.component_scores[weakest] < 80]
    if len(supporting) < min(2, len(recent)):
        return PracticeRecommendation(trainee_id=trainee_id, competency=weakest, scenario_id=None,
            rationale=f"The lowest recent component is {weakest} (mean {means[weakest]:.1f}/100), but repeated low evidence is not sufficient to select remediation. Complete another comparable assessment.",
            evidence_assessment_ids=[item.assessment_id for item in recent])
    tag = COMPETENCY_TO_SCENARIO_TAG.get(weakest, weakest)
    candidates = [(sid, sc) for sid, sc in scenarios.items() if tag in sc.get("learning_objectives", [])]
    if not candidates:
        return PracticeRecommendation(trainee_id=trainee_id, competency=weakest, scenario_id=None,
            rationale=f"Evidence indicates a gap in {weakest}, but no approved scenario targets that competency.",
            evidence_assessment_ids=[item.assessment_id for item in supporting])
    levels = {"beginner": 0, "intermediate": 1, "advanced": 2, "professional": 3}
    sid, sc = sorted(candidates, key=lambda pair: (levels.get(str(pair[1].get("difficulty_band","beginner")).lower(), 0), pair[0]))[0]
    return PracticeRecommendation(trainee_id=trainee_id, competency=weakest, scenario_id=sid,
        rationale=f"Recent assessment evidence shows repeated weakness in {weakest} (mean {means[weakest]:.1f}/100). Recommended scenario {sid} targets {tag} at the {sc.get('difficulty_band','unspecified')} level.",
        evidence_assessment_ids=[item.assessment_id for item in supporting])
