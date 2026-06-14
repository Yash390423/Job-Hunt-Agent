"""Tests for the resume-job matching service."""

from services.matching import calculate_match_score, extract_keywords


def test_calculate_match_score_prefers_similar_text():
    resume = "Python data analyst with dashboards, SQL, and reporting experience."
    job = "Seeking a Python data analyst skilled in SQL reporting and dashboards."
    unrelated = "Warehouse forklift operator with inventory handling experience."

    similar_score = calculate_match_score(resume, job)
    unrelated_score = calculate_match_score(resume, unrelated)

    assert similar_score > unrelated_score
    assert 0 <= similar_score <= 100


def test_extract_keywords_returns_terms():
    keywords = extract_keywords("Python SQL dashboards reporting analytics")

    assert isinstance(keywords, list)
    assert keywords
