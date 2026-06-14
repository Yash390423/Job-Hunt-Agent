"""Application tracking helpers for CSV and database persistence."""

from __future__ import annotations

import csv
import datetime
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_LOG_PATH = DATA_DIR / "applications_log.csv"
DEFAULT_COVER_LETTER_DIR = DATA_DIR / "cover_letters"


def _read_text_with_fallbacks(path: Path) -> str:
    """Read text using a small set of encodings that may appear in old logs."""
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    # Last resort: preserve as much as possible instead of crashing the app.
    return path.read_text(encoding="utf-8", errors="replace")


def _sanitize_job_title(job_title: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", job_title.strip())


def _job_hash(job_title: str, company: str) -> str:
    from models.database import Application

    return Application.create_job_hash(job_title, company)


def load_application_history(filepath: str | os.PathLike[str] = DEFAULT_LOG_PATH) -> list[dict[str, str]]:
    """Load the CSV application log into a normalized list of records."""
    path = Path(filepath)
    if not path.exists():
        return []

    records: list[dict[str, str]] = []
    csv_text = _read_text_with_fallbacks(path)
    reader = csv.DictReader(csv_text.splitlines())
    for row in reader:
        job_title = (row.get("Job Title") or row.get("job_title") or "").strip()
        agency = (row.get("Agency") or row.get("company") or "").strip()
        if not job_title or not agency:
            continue
        records.append(
            {
                "job_title": job_title,
                "company": agency,
                "job_hash": _job_hash(job_title, agency),
            }
        )
    return records


def save_cover_letter_file(
    job_title: str,
    cover_letter: str,
    directory: str | os.PathLike[str] = DEFAULT_COVER_LETTER_DIR,
) -> Path:
    """Persist a generated cover letter to disk."""
    directory_path = Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)
    filename = f"{_sanitize_job_title(job_title)}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = directory_path / filename
    filepath.write_text(cover_letter, encoding="utf-8")
    return filepath


def _save_application_to_db(
    job_title: str,
    agency: str,
    resume_summary: str,
    *,
    job_description: str | None = None,
    cover_letter: str | None = None,
    outreach_message: str | None = None,
    status: str = "applied",
    match_score: float | None = None,
) -> None:
    """Best-effort persistence into the SQLAlchemy database."""
    try:
        from sqlalchemy.exc import IntegrityError

        from models.database import Application, SessionLocal, create_tables
    except Exception:
        return

    create_tables()
    session = SessionLocal()
    try:
        application = Application(
            job_title=job_title.strip(),
            company=agency.strip(),
            job_description=job_description,
            resume_summary=resume_summary.strip(),
            cover_letter=cover_letter,
            outreach_message=outreach_message,
            status=status,
            match_score=match_score,
            job_hash=Application.create_job_hash(job_title, agency),
        )
        session.add(application)
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()


def log_llm_usage(
    agent_type: str,
    *,
    provider: str | None = None,
    model_name: str | None = None,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
    execution_time_ms: int | None = None,
) -> None:
    """Persist lightweight LLM usage metadata."""
    try:
        from models.database import LLMUsage, SessionLocal, create_tables
    except Exception:
        return

    create_tables()
    session = SessionLocal()
    try:
        session.add(
            LLMUsage(
                agent_type=agent_type,
                provider=provider,
                model_name=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                execution_time_ms=execution_time_ms,
            )
        )
        session.commit()
    finally:
        session.close()


def log_application(
    job_title: str,
    agency: str,
    resume_summary: str,
    filepath: str | os.PathLike[str] = DEFAULT_LOG_PATH,
    *,
    job_description: str | None = None,
    cover_letter: str | None = None,
    outreach_message: str | None = None,
    status: str = "applied",
    match_score: float | None = None,
) -> None:
    """Write the application to CSV and the optional SQL database."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not exists:
            writer.writerow(["Job Title", "Agency", "ResumeSummary", "DateApplied"])
        writer.writerow(
            [
                job_title.strip(),
                agency.strip(),
                resume_summary.strip()[:150],
                datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            ]
        )

    _save_application_to_db(
        job_title,
        agency,
        resume_summary,
        job_description=job_description,
        cover_letter=cover_letter,
        outreach_message=outreach_message,
        status=status,
        match_score=match_score,
    )
