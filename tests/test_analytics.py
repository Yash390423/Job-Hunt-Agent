"""Tests for analytics calculations."""

from models.database import Application, LLMUsage, SessionLocal, create_tables
from services.analytics import get_application_stats, get_llm_stats, get_top_companies


def test_application_stats_and_top_companies():
    create_tables()

    with SessionLocal() as db:
        db.add_all(
            [
                Application(
                    job_title="Data Analyst",
                    company="Example Corp",
                    job_description="Analyze data.",
                    resume_summary="Strong analytics background.",
                    cover_letter="Cover letter",
                    outreach_message="Message",
                    status="responded",
                    match_score=82.5,
                    job_hash=Application.create_job_hash("Data Analyst", "Example Corp"),
                ),
                Application(
                    job_title="BI Analyst",
                    company="Example Corp",
                    job_description="Build dashboards.",
                    resume_summary="BI experience.",
                    cover_letter="Cover letter",
                    outreach_message="Message",
                    status="applied",
                    match_score=67.0,
                    job_hash=Application.create_job_hash("BI Analyst", "Example Corp"),
                ),
            ]
        )
        db.add(
            LLMUsage(
                agent_type="job_application_pipeline",
                provider="gemini",
                model_name="gemini-2.5-flash",
                execution_time_ms=1200,
            )
        )
        db.commit()

    stats = get_application_stats()
    llm_stats = get_llm_stats()
    companies = get_top_companies()

    assert stats["total_applications"] == 2
    assert stats["responses"] == 1
    assert stats["average_match_score"] > 0
    assert llm_stats["executions"] == 1
    assert companies[0]["company"] == "Example Corp"
