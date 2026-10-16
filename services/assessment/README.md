# SENTINEL-X Assessment Service

FastAPI service for scenario metadata, session events, deterministic scoring, trainee progress, practice recommendations, and after-action review.

## Requirements

- Python 3.11+
- Dependencies declared in this directory's `pyproject.toml`

## Install and run

From the repository root:

```bash
python -m venv .venv
```

Activate the environment, then install:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -e "services/assessment[dev]"

# Linux/macOS
source .venv/bin/activate
python -m pip install -e "services/assessment[dev]"
```

Run the service from this directory:

```bash
cd services/assessment
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the API schema. The default development bind address is loopback; do not expose this prototype on a shared network before authentication, authorization, transport security, and deployment controls are implemented and reviewed.

## Tests and quality checks

Run from `services/assessment`:

```bash
python -m pip install -e ".[dev]"
ruff check app tests
ruff format --check app tests
mypy app
pytest
```

All included training scenarios and sample events are synthetic. Rubric weights are provisional and are not an approved grading standard.
