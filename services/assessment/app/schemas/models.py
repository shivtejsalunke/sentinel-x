"""Request and response contracts shared by the API and assessment modules."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class CreateSessionRequest(StrictModel):
    trainee_id: str = Field(min_length=1, max_length=120)
    scenario_id: str = Field(min_length=1, max_length=120)
    seed: int = Field(ge=0, le=2**32 - 1)

class SessionRecord(StrictModel):
    session_id: str = Field(default_factory=lambda: new_id("ses"))
    trainee_id: str
    scenario_id: str
    scenario_version: str
    rubric_id: str
    rubric_version: str
    seed: int
    status: Literal["READY", "RUNNING", "COMPLETED", "REVIEWED"] = "RUNNING"
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None

class EventPayload(StrictModel):
    observation_id: str = Field(min_length=1, max_length=120)
    response_category: str = Field(min_length=1, max_length=80)
    confidence: float = Field(ge=0.0, le=1.0)

class CreateEventRequest(StrictModel):
    sequence_number: int = Field(ge=1)
    scenario_time_ms: int = Field(ge=0)
    event_type: Literal["classification_submitted"]
    payload: EventPayload

class EventRecord(StrictModel):
    event_id: str = Field(default_factory=lambda: new_id("evt"))
    session_id: str
    sequence_number: int
    scenario_time_ms: int
    event_type: str
    payload: dict[str, Any]
    created_at: datetime = Field(default_factory=utc_now)

class MetricValue(StrictModel):
    value: float | None
    numerator: float | None = None
    denominator: float | None = None
    unit: str = "ratio"
    status: Literal["available", "not_available"] = "available"

class AssessmentResult(StrictModel):
    assessment_id: str = Field(default_factory=lambda: new_id("asm"))
    session_id: str
    scenario_id: str
    scenario_version: str
    rubric_id: str
    rubric_version: str
    overall_score: float
    component_scores: dict[str, float]
    metrics: dict[str, MetricValue]
    error_categories: list[str] = Field(default_factory=list)
    critical_flags: list[str] = Field(default_factory=list)
    event_ids: list[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=utc_now)

class RecommendationRequest(StrictModel):
    trainee_id: str = Field(min_length=1, max_length=120)

class PracticeRecommendation(StrictModel):
    recommendation_id: str = Field(default_factory=lambda: new_id("rec"))
    trainee_id: str
    competency: str | None
    scenario_id: str | None
    rationale: str
    evidence_assessment_ids: list[str] = Field(default_factory=list)
    policy_version: str = "rules-v1"
    created_at: datetime = Field(default_factory=utc_now)

class ProgressResponse(StrictModel):
    trainee_id: str
    completed_sessions: int
    latest_score: float | None
    mean_score: float | None
    competency_means: dict[str, float]
