from __future__ import annotations

def test_health_and_public_scenario_do_not_expose_answer_key(service_client):
    client=service_client
    assert client.get("/health").json()["status"]=="ok"
    response=client.get("/api/v1/scenarios/OBS-001")
    assert response.status_code==200
    body=response.json()
    assert "observations" not in body and "answer_key" not in body
    assert body["observation_count"]==3

def test_complete_training_workflow(service_client):
    client=service_client
    created=client.post("/api/v1/sessions",json={"trainee_id":"trainee-demo","scenario_id":"OBS-001","seed":104729})
    assert created.status_code==201,created.text
    session_id=created.json()["session_id"]
    events=[("obs-001","category_a",0.8),("obs-002","category_b",0.7),("obs-003","no_observation",0.9)]
    for seq,(oid,category,confidence) in enumerate(events,start=1):
        response=client.post(f"/api/v1/sessions/{session_id}/events",json={"sequence_number":seq,
            "scenario_time_ms":seq*10000,"event_type":"classification_submitted",
            "payload":{"observation_id":oid,"response_category":category,"confidence":confidence}})
        assert response.status_code==201,response.text
    completed=client.post(f"/api/v1/sessions/{session_id}/complete")
    assert completed.status_code==200,completed.text
    result=completed.json()
    assert result["metrics"]["classification_accuracy"]["value"]==1.0
    assert client.post(f"/api/v1/sessions/{session_id}/complete").json()["assessment_id"]==result["assessment_id"]
    aar=client.get(f"/api/v1/sessions/{session_id}/aar")
    assert aar.status_code==200 and len(aar.json()["timeline"])==3
    assert client.get("/api/v1/trainees/trainee-demo/progress").json()["completed_sessions"]==1

def test_duplicate_event_sequence_is_rejected(service_client):
    client=service_client
    session=client.post("/api/v1/sessions",json={"trainee_id":"trainee-demo","scenario_id":"OBS-001","seed":7}).json()
    payload={"sequence_number":1,"scenario_time_ms":1000,"event_type":"classification_submitted",
        "payload":{"observation_id":"obs-001","response_category":"category_a","confidence":0.8}}
    assert client.post(f"/api/v1/sessions/{session['session_id']}/events",json=payload).status_code==201
    payload["scenario_time_ms"]=1500
    assert client.post(f"/api/v1/sessions/{session['session_id']}/events",json=payload).status_code==409

def test_invalid_observation_and_unknown_scenario_are_rejected(service_client):
    client=service_client
    missing=client.post("/api/v1/sessions",json={"trainee_id":"trainee-demo","scenario_id":"UNKNOWN","seed":1})
    assert missing.status_code==404
    session=client.post("/api/v1/sessions",json={"trainee_id":"trainee-demo","scenario_id":"OBS-001","seed":1}).json()
    bad=client.post(f"/api/v1/sessions/{session['session_id']}/events",json={"sequence_number":1,
        "scenario_time_ms":1000,"event_type":"classification_submitted",
        "payload":{"observation_id":"missing","response_category":"category_a","confidence":0.5}})
    assert bad.status_code==422
