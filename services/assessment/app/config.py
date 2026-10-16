"""Runtime configuration for the local assessment service."""
from __future__ import annotations
import os
from pathlib import Path

def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]

def data_directory() -> Path:
    configured = os.getenv("SENTINEL_X_DATA_DIR")
    path = Path(configured).expanduser() if configured else Path.cwd() / "var"
    path.mkdir(parents=True, exist_ok=True)
    return path

def database_path() -> Path:
    configured = os.getenv("SENTINEL_X_DATABASE_PATH")
    if configured:
        path = Path(configured).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    return data_directory() / "sentinel-x.sqlite3"

def scenario_directory() -> Path:
    configured = os.getenv("SENTINEL_X_SCENARIO_DIR")
    if configured:
        return Path(configured).expanduser()
    return repository_root() / "scenarios" / "approved"
