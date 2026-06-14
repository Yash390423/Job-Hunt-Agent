"""Initialize database and create tables."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "job_hunt_assistant"
for path in (str(REPO_ROOT), str(APP_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from models.database import create_tables
from utils.logger import logger


if __name__ == "__main__":
    try:
        logger.info("Initializing database...")
        create_tables()
        logger.info("Database initialized successfully.")
        print("Database tables created!")
    except Exception as exc:
        logger.error(f"Failed to initialize database: {exc}")
        print(f"Error: {exc}")
        sys.exit(1)
