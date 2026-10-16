#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/../services/assessment"
python -m pip install -e ".[dev]"
ruff check app tests --select F
mypy app
pytest
