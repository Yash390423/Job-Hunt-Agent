"""Tests for job deduplication helpers."""

from services.deduplication import check_duplicate, create_job_hash


def test_create_job_hash_is_case_insensitive():
    assert create_job_hash("Data Analyst", "Example Corp") == create_job_hash(
        "data analyst",
        "example corp",
    )


def test_check_duplicate_matches_existing_application():
    existing = [{"job_title": "Data Analyst", "company": "Example Corp"}]

    assert check_duplicate(existing, "data analyst", "example corp") is True
    assert check_duplicate(existing, "product manager", "example corp") is False
