#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/../services/assessment"
python -m pip install -e ".[dev]"
ruff check app tests
ruff format --check app tests
mypy app
pytest
