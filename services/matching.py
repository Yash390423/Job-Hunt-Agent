"""Resume-JD matching algorithm."""

from __future__ import annotations

import math
import re
from collections import Counter


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _cosine_similarity_from_counts(count_a: Counter[str], count_b: Counter[str]) -> float:
    shared_terms = set(count_a) | set(count_b)
    dot_product = sum(count_a[term] * count_b[term] for term in shared_terms)
    magnitude_a = math.sqrt(sum(value * value for value in count_a.values()))
    magnitude_b = math.sqrt(sum(value * value for value in count_b.values()))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


def calculate_match_score(resume_text: str, job_description: str) -> float:
    """Calculate similarity score between resume and job description."""
    if not resume_text or not job_description:
        return 0.0

    if not resume_text.strip() or not job_description.strip():
        return 0.0

    resume_tokens = _tokenize(resume_text)
    job_tokens = _tokenize(job_description)
    if not resume_tokens or not job_tokens:
        return 0.0

    similarity = _cosine_similarity_from_counts(Counter(resume_tokens), Counter(job_tokens))
    return round(float(similarity) * 100, 2)


def extract_keywords(text: str) -> list:
    """Extract important keywords from text."""
    if not text:
        return []

    tokens = [token for token in _tokenize(text) if len(token) > 2]
    ranked_tokens = [token for token, _ in Counter(tokens).most_common(20)]
    return ranked_tokens
