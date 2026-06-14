"""Analytics calculations for applications and LLM usage."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import func

from models.database import Application, LLMUsage, SessionLocal


def get_application_stats(days: int = 30) -> dict[str, float | int]:
    """Get application statistics for the last N days."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    with SessionLocal() as db:
        total_apps = db.query(Application).filter(Application.created_at >= cutoff_date).count()
        responded = (
            db.query(Application)
            .filter(Application.status == "responded", Application.created_at >= cutoff_date)
            .count()
        )
        avg_match_score = (
            db.query(func.avg(Application.match_score))
            .filter(Application.created_at >= cutoff_date)
            .scalar()
        )

    response_rate = (responded / total_apps * 100) if total_apps > 0 else 0

    return {
        "total_applications": total_apps,
        "responses": responded,
        "response_rate": round(response_rate, 2),
        "average_match_score": round(float(avg_match_score or 0), 2),
        "period_days": days,
    }


def get_top_companies(limit: int = 10) -> list[dict[str, int | str]]:
    """Get the companies that received the most applications."""
    with SessionLocal() as db:
        results = (
            db.query(Application.company, func.count(Application.id).label("count"))
            .group_by(Application.company)
            .order_by(func.count(Application.id).desc())
            .limit(limit)
            .all()
        )

    return [{"company": company, "count": count} for company, count in results]


def get_llm_stats(days: int = 30) -> dict[str, float | int]:
    """Summarize LLM usage for dashboard metrics."""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    with SessionLocal() as db:
        executions = db.query(LLMUsage).filter(LLMUsage.created_at >= cutoff_date).count()
        avg_execution_time = (
            db.query(func.avg(LLMUsage.execution_time_ms))
            .filter(LLMUsage.created_at >= cutoff_date)
            .scalar()
        )

    return {
        "executions": executions,
        "average_execution_time_ms": round(float(avg_execution_time or 0), 2),
        "period_days": days,
    }
