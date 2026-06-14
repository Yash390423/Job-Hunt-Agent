"""Job deduplication logic."""

from __future__ import annotations

import hashlib


def create_job_hash(job_title: str, company: str) -> str:
    """Create a unique hash for a job posting."""
    job_key = f"{job_title.lower().strip()}_{company.lower().strip()}"
    return hashlib.md5(job_key.encode()).hexdigest()


def check_duplicate(existing_applications: list, new_job_title: str, new_company: str) -> bool:
    """Check if job already applied to."""
    new_hash = create_job_hash(new_job_title, new_company)
    
    for app in existing_applications:
        existing_hash = create_job_hash(app.get("job_title", ""), app.get("company", ""))
        if new_hash == existing_hash:
            return True
    
    return False
