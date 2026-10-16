"""FastAPI application for SENTINEL-X's local assessment workflow."""
from __future__ import annotations
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, HTTPException, status
from app.adaptation.engine import recommend_practice
from app.aar.generator import generate_aar
from app.config import database_path
from app.persistence.database import Repository
from app.scenarios import ScenarioError, ground_truth_for_session, load_scenarios, public_scenario
from app.schemas.models import AssessmentResult, CreateEventRequest, CreateSessionRequest, EventRecord, PracticeRecommendation, ProgressResponse, RecommendationRequest, SessionRecord
from app.scoring.engine import RUBRIC_ID, RUBRIC_VERSION, score_session
from app.security.policy import validate_identifier

@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.repository=Repository(database_path())
    application.state.scenarios=load_scenarios()
    yield

app=FastAPI(title="SENTINEL-X Assessment API",version="0.1.0",
    description="Local-first synthetic training assessment, deterministic scoring, adaptive practice, and AAR. Not connected to live aircraft or operational equipment.",
    lifespan=lifespan)

def repository() -> Repository:
    repo=getattr(app.state,"repository",None)
    if repo is None:
        repo=Repository(database_path()); app.state.repository=repo
    return repo

def scenarios() -> dict[str,dict[str,Any]]:
    configured=getattr(app.state,"scenarios",None)
    if configured is None:
        try: configured=load_scenarios()
        except ScenarioError as exc: raise HTTPException(status_code=500,detail=f"scenario_catalog_invalid: {exc}") from exc
        app.state.scenarios=configured
    return configured

def get_session_or_404(session_id: str) -> SessionRecord:
    try: validate_identifier(session_id)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    item=repository().get_session(session_id)
    if item is None: raise HTTPException(status_code=404,detail="session_not_found")
    return item

@app.get("/health")
def health() -> dict[str,str]:
    return {"status":"ok","service":"sentinel-x-assessment"}

@app.get("/api/v1/scenarios")
def list_scenarios() -> list[dict[str,Any]]:
    return [public_scenario(item) for item in scenarios().values()]

@app.get("/api/v1/scenarios/{scenario_id}")
def get_scenario(scenario_id: str) -> dict[str,Any]:
    try: validate_identifier(scenario_id)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    item=scenarios().get(scenario_id)
    if item is None: raise HTTPException(status_code=404,detail="scenario_not_found")
    return public_scenario(item)

@app.get("/api/v1/scenarios/{scenario_id}/observations")
def get_scenario_observations(scenario_id: str) -> dict[str, Any]:
    """Return trainee-facing prompts without scoring ground truth."""
    try:
        validate_identifier(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    scenario = scenarios().get(scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="scenario_not_found")
    return {
        "scenario_id": scenario_id,
        "version": scenario["version"],
        "allowed_response_categories": scenario.get("allowed_response_categories", []),
        "observations": [
            {
                "observation_id": item["observation_id"],
                "display_prompt": item.get("display_prompt", "Complete the assigned observation."),
            }
            for item in scenario["observations"]
        ],
    }


@app.post("/api/v1/sessions",response_model=SessionRecord,status_code=status.HTTP_201_CREATED)
def create_session(request: CreateSessionRequest) -> SessionRecord:
    for name,value in (("trainee_id",request.trainee_id),("scenario_id",request.scenario_id)):
        try: validate_identifier(value)
        except ValueError as exc: raise HTTPException(status_code=422,detail={"field":name,"message":str(exc)}) from exc
    scenario=scenarios().get(request.scenario_id)
    if scenario is None: raise HTTPException(status_code=404,detail="scenario_not_found")
    record=SessionRecord(trainee_id=request.trainee_id,scenario_id=request.scenario_id,
        scenario_version=scenario["version"],rubric_id=scenario.get("rubric_id",RUBRIC_ID),
        rubric_version=scenario.get("rubric_version",RUBRIC_VERSION),seed=request.seed)
    try: return repository().create_session(record)
    except Exception as exc: raise HTTPException(status_code=500,detail="session_persistence_failed") from exc

@app.post("/api/v1/sessions/{session_id}/events",response_model=EventRecord,status_code=status.HTTP_201_CREATED)
def append_event(session_id: str, request: CreateEventRequest) -> EventRecord:
    session=get_session_or_404(session_id); scenario=scenarios().get(session.scenario_id)
    if scenario is None: raise HTTPException(status_code=500,detail="session_scenario_unavailable")
    if request.payload.observation_id not in {o["observation_id"] for o in scenario["observations"]}:
        raise HTTPException(status_code=422,detail="observation_id_not_in_scenario")
    if request.payload.response_category not in scenario.get("allowed_response_categories",[]):
        raise HTTPException(status_code=422,detail="response_category_not_allowed")
    event=EventRecord(session_id=session.session_id,sequence_number=request.sequence_number,
        scenario_time_ms=request.scenario_time_ms,event_type=request.event_type,payload=request.payload.model_dump())
    try: return repository().append_event(event)
    except LookupError as exc: raise HTTPException(status_code=404,detail=str(exc)) from exc
    except ValueError as exc: raise HTTPException(status_code=409,detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=500,detail="event_persistence_failed") from exc

@app.post("/api/v1/sessions/{session_id}/complete",response_model=AssessmentResult)
def complete_session(session_id: str) -> AssessmentResult:
    session=get_session_or_404(session_id); repo=repository()
    existing=repo.get_assessment(session_id)
    if existing is not None: return existing
    if session.status != "RUNNING": raise HTTPException(status_code=409,detail="session_not_running")
    scenario=scenarios().get(session.scenario_id)
    if scenario is None: raise HTTPException(status_code=500,detail="session_scenario_unavailable")
    events = repo.get_events(session_id)
    submitted = {event.payload.get("observation_id") for event in events}
    required = {item["observation_id"] for item in scenario["observations"]}
    missing = sorted(required - submitted)
    if missing:
        raise HTTPException(
            status_code=409,
            detail={"code": "session_observations_incomplete", "missing_observation_ids": missing},
        )
    result=score_session(session,events,ground_truth_for_session(scenario,session.seed))
    try: return repo.complete_session(session_id,result)
    except LookupError as exc: raise HTTPException(status_code=404,detail=str(exc)) from exc
    except ValueError as exc: raise HTTPException(status_code=409,detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=500,detail="assessment_persistence_failed") from exc

@app.get("/api/v1/sessions/{session_id}/assessment",response_model=AssessmentResult)
def get_assessment(session_id: str) -> AssessmentResult:
    get_session_or_404(session_id); result=repository().get_assessment(session_id)
    if result is None: raise HTTPException(status_code=409,detail="assessment_not_available")
    return result

@app.get("/api/v1/sessions/{session_id}/aar")
def get_aar(session_id: str) -> dict[str,Any]:
    session=get_session_or_404(session_id); repo=repository(); assessment=repo.get_assessment(session_id)
    if assessment is None: raise HTTPException(status_code=409,detail="assessment_not_available")
    return generate_aar(session,assessment,repo.get_events(session_id))

@app.get("/api/v1/trainees/{trainee_id}/progress",response_model=ProgressResponse)
def get_progress(trainee_id: str) -> ProgressResponse:
    try: validate_identifier(trainee_id)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    repo=repository(); sessions=repo.list_sessions_for_trainee(trainee_id); assessments=repo.list_assessments_for_trainee(trainee_id)
    scores=[a.overall_score for a in assessments]; names=sorted({key for a in assessments for key in a.component_scores})
    means={name:round(sum(a.component_scores[name] for a in assessments if name in a.component_scores)/
        sum(1 for a in assessments if name in a.component_scores),4) for name in names if any(name in a.component_scores for a in assessments)}
    return ProgressResponse(trainee_id=trainee_id,completed_sessions=sum(s.status in {"COMPLETED","REVIEWED"} for s in sessions),
        latest_score=scores[-1] if scores else None,mean_score=round(sum(scores)/len(scores),4) if scores else None,
        competency_means=means)

@app.post("/api/v1/recommendations",response_model=PracticeRecommendation)
def create_recommendation(request: RecommendationRequest) -> PracticeRecommendation:
    try: validate_identifier(request.trainee_id)
    except ValueError as exc: raise HTTPException(status_code=422,detail=str(exc)) from exc
    repo=repository(); rec=recommend_practice(request.trainee_id,repo.list_assessments_for_trainee(request.trainee_id),scenarios())
    try: repo.save_recommendation(rec)
    except Exception as exc: raise HTTPException(status_code=500,detail="recommendation_persistence_failed") from exc
    return rec
