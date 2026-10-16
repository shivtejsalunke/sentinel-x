# SENTINEL-X

[![Assessment Service CI](https://github.com/shivtejsalunke/sentinel-x/actions/workflows/assessment-ci.yml/badge.svg?branch=main)](https://github.com/shivtejsalunke/sentinel-x/actions/workflows/assessment-ci.yml)


**Adaptive simulation, training assessment, and readiness platform**

SENTINEL-X is a desktop-first training system for controlled, reproducible simulation exercises. It connects scenario configuration, simulated observations, structured trainee decisions, deterministic assessment, after-action review (AAR), and targeted practice recommendations in one auditable workflow.

The initial software baseline is local-first. The assessment service and scenario contracts can be tested independently of a 3D client; Unity is the intended simulation client, with source scaffolding under `simulation/`. No live aircraft, operational counter-drone equipment, or real-world autonomous control is connected.

## Core workflow

1. Select and validate a versioned training scenario.
2. Start a session using a recorded scenario seed.
3. Record observations and trainee decisions as ordered events.
4. Evaluate the session against a versioned, deterministic rubric.
5. Persist the result and evidence in a local SQLite database.
6. Generate an AAR tied to recorded events and scoring components.
7. Recommend follow-up practice from demonstrated competency gaps.
8. Compare equivalent assessments only when scenario and rubric compatibility is established.

## Repository map

```text
sentinel-x/
├── README.md
├── LICENSES.md
├── docs/                         # Requirements, architecture, threat model, tests, compliance
├── simulation/                   # Unity/C# client scaffolding and test guidance
├── services/assessment/           # FastAPI service, schemas, scoring, adaptation, AAR, SQLite
├── scenarios/                     # JSON Schema, approved examples, test fixtures
├── datasets/                      # Synthetic event data and provenance manifests
├── reports/                       # Local validation outputs (no personal or operational data)
├── scripts/                       # Development and validation helpers
└── .github/workflows/             # Automated Python checks
```

## Current implementation

| Component | Status in this repository |
|---|---|
| Scenario schema and sample scenarios | Implemented |
| Session/event contracts and validation | Implemented |
| Deterministic assessment and metrics | Implemented |
| Rules-based practice recommendations | Implemented |
| Evidence-linked AAR generation | Implemented |
| SQLite persistence and API endpoints | Implemented |
| Unit tests and CI workflow | Implemented; CI runs on GitHub |
| Unity project, 3D scene, simulation assets | Integration scaffold only; create/open with a supported Unity LTS editor |
| Validated real-world sensor models or operational AI | Not implemented |
| Training efficacy evidence | Not established; requires a controlled evaluation |

The assessment weights in `services/assessment/app/scoring/engine.py` are provisional prototype values, not an institutionally approved rubric. They are versioned and must be reviewed by qualified training personnel before formal use.

## Requirements

- Python 3.11 or newer
- Git
- Optional: Unity Hub and a supported Unity LTS editor for the 3D client workstream

The assessment service does not require a cloud account, external AI API, or network connection after dependencies are installed.

## Quick start

From the repository root:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

Install the service and development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Start the API from the assessment directory:

```bash
cd services/assessment
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the local OpenAPI interface and `http://127.0.0.1:8000/health` for a health check. The service binds to loopback by default in these instructions; do not expose it to a network without implementing and reviewing production authentication, authorization, transport security, request limits, and deployment controls.

## Example API workflow

### 1. List scenarios

```bash
curl http://127.0.0.1:8000/api/v1/scenarios
```

### 2. Create a session

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"trainee_id":"trainee-demo","scenario_id":"OBS-001","seed":104729}'
```

Use the `session_id` returned by the response in subsequent calls. Scenario ground truth is held by the assessment service and is not returned by the public scenario listing.

### 3. Record a decision

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sessions/SESSION_ID/events \
  -H "Content-Type: application/json" \
  -d '{"sequence_number":1,"scenario_time_ms":12000,"event_type":"classification_submitted","payload":{"observation_id":"obs-001","response_category":"category_b","confidence":0.65}}'
```

The response category above is illustrative. See the approved scenario package for the expected task format.

### 4. Complete, assess, and review

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sessions/SESSION_ID/complete
curl http://127.0.0.1:8000/api/v1/sessions/SESSION_ID/assessment
curl http://127.0.0.1:8000/api/v1/sessions/SESSION_ID/aar
curl -X POST http://127.0.0.1:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"trainee_id":"trainee-demo"}'
```

Replace `SESSION_ID` with the returned identifier. For detailed contracts, see `docs/architecture.md` and the Pydantic schemas in `services/assessment/app/schemas/`.

## Configuration

- `SENTINEL_X_DATA_DIR`: location for the SQLite database. Defaults to `./var` for local development.
- `SENTINEL_X_DATABASE_PATH`: explicit SQLite database path; takes precedence over the data directory.
- `SENTINEL_X_SCENARIO_DIR`: scenario package location. Defaults to the repository's `scenarios/approved` directory when run from a normal source checkout.

Use synthetic identifiers in development. Do not commit trainee personal data, access tokens, secrets, logs with sensitive content, operational material, generated builds, or database files.

## Engineering principles

- **Deterministic grading:** scoring is ordinary tested code, not an LLM judgment.
- **Traceability:** results store scenario and rubric versions and reference session events.
- **Reproducibility:** every session stores its scenario seed and version.
- **Fail closed:** invalid scenarios, duplicate event sequence numbers, and unauthorized data access must be rejected.
- **Human oversight:** institutional scoring rules and newly authored scenarios require appropriate review.
- **Offline-first:** core assessment and reporting are designed to run locally.
- **No unsupported claims:** the repository does not claim defence accreditation, certified sensor fidelity, model accuracy, or learning improvement without external validation.

## Development checks

```bash
ruff check services/assessment
ruff format --check services/assessment
mypy services/assessment/app
pytest
```

GitHub Actions runs the automated quality checks on pushes and pull requests. The Unity scaffolding is not compiled by this Python workflow; add Unity Test Framework Edit Mode and Play Mode jobs when a complete Unity project and required licensing/runner configuration are available.

## Documentation

- `docs/requirements.md` — scope and acceptance criteria
- `docs/architecture.md` — modules, data flow, API, persistence, and boundaries
- `docs/threat-model.md` — assets, trust boundaries, threats, controls, and residual risks
- `docs/test-plan.md` — test strategy and release gates
- `docs/compliance-register.md` — applicability checks and evidence register
- `docs/decisions/` — architecture decision records
- `LICENSES.md` — project and dependency/asset licensing notes

## Limitations and intended use

This is a software training and assessment prototype. It is not an operational command-and-control system, sensor-certified simulator, autonomous aircraft controller, or substitute for authorized instructor-led practical training. The scenario taxonomies and score weights are illustrative until approved for a defined curriculum. Any real hardware integration requires a separate safety, security, legal, and institutional review.
