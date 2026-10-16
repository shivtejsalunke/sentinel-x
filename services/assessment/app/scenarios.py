"""Scenario package loading and public/private metadata separation."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from app.config import scenario_directory

class ScenarioError(ValueError):
    """Scenario package could not be loaded or validated."""

def load_scenarios(directory: Path | None = None) -> dict[str, dict[str, Any]]:
    target=directory or scenario_directory()
    scenarios: dict[str, dict[str,Any]]={}
    if not target.exists(): return scenarios
    for path in sorted(p for p in target.glob("*.json") if p.is_file()):
        try: raw=json.loads(path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError) as exc: raise ScenarioError(f"invalid scenario file {path.name}: {exc}") from exc
        required={"scenario_id","version","title","rubric_id","rubric_version","difficulty_band","learning_objectives","observations","allowed_response_categories","environment"}
        missing=required.difference(raw)
        if missing: raise ScenarioError(f"scenario {path.name} missing fields: {', '.join(sorted(missing))}")
        if raw["scenario_id"] in scenarios: raise ScenarioError(f"duplicate scenario_id: {raw['scenario_id']}")
        if not isinstance(raw["observations"],list) or not raw["observations"]: raise ScenarioError(f"scenario {path.name} must define observations")
        seen=set()
        for observation in raw["observations"]:
            if not isinstance(observation,dict) or not {"observation_id","expected_category","is_relevant"}.issubset(observation):
                raise ScenarioError(f"scenario {path.name} has invalid observation")
            oid=observation["observation_id"]
            if not isinstance(oid,str) or not oid or oid in seen: raise ScenarioError(f"scenario {path.name} has duplicate/invalid observation_id")
            seen.add(oid)
        scenarios[raw["scenario_id"]]=raw
    return scenarios

def public_scenario(scenario: dict[str,Any]) -> dict[str,Any]:
    public={key:value for key,value in scenario.items() if key not in {"observations","ground_truth","answer_key"}}
    public["observation_count"]=len(scenario.get("observations",[]))
    public["observation_ids"]=[item["observation_id"] for item in scenario.get("observations",[])]
    return public

def ground_truth_for_session(scenario: dict[str,Any], seed: int) -> dict[str,Any]:
    """Expose configured synthetic ground truth only to the assessment path."""
    del seed  # Seeded variation belongs to the simulation client integration workstream.
    return {"observations":{item["observation_id"]:{"expected_category":item["expected_category"],
        "is_relevant":item["is_relevant"]} for item in scenario["observations"]}}
