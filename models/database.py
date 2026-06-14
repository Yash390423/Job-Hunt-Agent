"""Database models and session management for the job hunt assistant."""

from __future__ import annotations

import os
import logging
from datetime import datetime
from hashlib import md5
from pathlib import Path

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()
logger = logging.getLogger(__name__)


def _default_database_url() -> str:
    """Return the configured database URL or a local SQLite fallback."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    sqlite_path = Path(__file__).resolve().parents[1] / "job_hunt.db"
    return f"sqlite:///{sqlite_path}"


def _create_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(
        database_url,
        connect_args=connect_args,
        future=True,
        pool_pre_ping=True,
    )


def _build_engine_with_fallback():
    configured_url = _default_database_url()
    if configured_url.startswith("sqlite"):
        return configured_url, _create_engine(configured_url)

    try:
        candidate = _create_engine(configured_url)
        with candidate.connect():
            pass
        return configured_url, candidate
    except OperationalError:
        sqlite_path = Path(__file__).resolve().parents[1] / "job_hunt.db"
        fallback_url = f"sqlite:///{sqlite_path}"
        logger.warning(
            "PostgreSQL unavailable at %s. Falling back to local SQLite database at %s.",
            configured_url,
            fallback_url,
        )
        return fallback_url, _create_engine(fallback_url)


DATABASE_URL, engine = _build_engine_with_fallback()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Application(Base):
    """Persisted job application details."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    job_description = Column(Text, nullable=True)
    resume_summary = Column(Text, nullable=True)
    cover_letter = Column(Text, nullable=True)
    outreach_message = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="applied")
    match_score = Column(Float, nullable=True)
    job_hash = Column(String(32), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"Application(job_title={self.job_title!r}, company={self.company!r})"

    @staticmethod
    def create_job_hash(job_title: str, company: str) -> str:
        """Create a stable hash for deduplication."""
        job_key = f"{job_title.lower().strip()}_{company.lower().strip()}"
        return md5(job_key.encode("utf-8")).hexdigest()


class LLMUsage(Base):
    """Persisted usage metrics for LLM calls."""

    __tablename__ = "llm_usage"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(100), nullable=False, index=True)
    provider = Column(String(100), nullable=True)
    model_name = Column(String(100), nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"LLMUsage(agent_type={self.agent_type!r}, provider={self.provider!r})"


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_session():
    """Create a new database session."""
    return SessionLocal()
