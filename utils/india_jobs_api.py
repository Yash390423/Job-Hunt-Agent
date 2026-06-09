import os
from time import sleep

import requests
from requests import RequestException

from .config import ADZUNA_APP_ID, ADZUNA_APP_KEY

ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def _normalize_job_result(job):
    location = job.get("location") or {}
    area = location.get("area") or []
    location_name = location.get("display_name") or ", ".join(
        part for part in area if part
    )

    company_name = (job.get("company") or {}).get("display_name") or "Unknown Company"
    title = job.get("title") or "Unknown Title"
    description = job.get("description") or ""
    redirect_url = job.get("redirect_url") or ""

    return {
        "MatchedObjectDescriptor": {
            "PositionTitle": title,
            "OrganizationName": company_name,
            "PositionLocation": (
                [{"LocationName": location_name}] if location_name else []
            ),
            "PositionURI": redirect_url,
            "PositionFormattedDescription": description,
            "QualificationSummary": description,
        },
        "raw": job,
    }


def fetch_india_jobs(keyword, location="India", results_per_page=5, country=ADZUNA_COUNTRY):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise ValueError(
            "ADZUNA_APP_ID and ADZUNA_APP_KEY must be configured in utils/.env."
        )

    api_url = f"{ADZUNA_BASE_URL}/{country}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": keyword,
        "where": location,
        "results_per_page": results_per_page,
        "content-type": "application/json",
        "sort_by": "date",
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "job-hunt-assistant",
    }

    last_error = None
    for attempt in range(3):
        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            jobs = data.get("results", [])
            return [_normalize_job_result(job) for job in jobs]
        except RequestException as exc:
            last_error = exc
            if attempt < 2:
                sleep(2 ** attempt)
                continue
            raise ConnectionError(
                f"India jobs API unreachable after 3 attempts: {exc.__class__.__name__}"
            ) from last_error
