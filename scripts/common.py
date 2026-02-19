from __future__ import annotations

import os
from pathlib import Path

from pymongo import MongoClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_env_file() -> None:
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> dict:
    load_env_file()
    return {
        "mongo_uri": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "mongo_db": os.getenv("MONGO_DB", "clinical_synth_demo"),
        "seed": int(os.getenv("SEED", "491")),
        "participants": int(os.getenv("PARTICIPANTS", "100")),
        "min_visits": int(os.getenv("MIN_VISITS", "3")),
        "max_visits": int(os.getenv("MAX_VISITS", "5")),
        "min_notes": int(os.getenv("MIN_NOTES", "1")),
        "max_notes": int(os.getenv("MAX_NOTES", "4")),
        "drop_existing": _as_bool(os.getenv("DROP_EXISTING"), default=True),
    }


def get_db(settings: dict):
    client = MongoClient(settings["mongo_uri"], serverSelectionTimeoutMS=5000)
    return client[settings["mongo_db"]], client
