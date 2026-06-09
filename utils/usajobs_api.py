import requests
from requests import RequestException
from time import sleep

from .config import USAJOBS_API_KEY


def fetch_usajobs(keyword, location="remote", results_per_page=5):
    if not USAJOBS_API_KEY:
        raise ValueError("USAJOBS_API_KEY is not configured.")

    api_url = "https://data.usajobs.gov/api/Search"

    headers = {
        "Authorization-Key": USAJOBS_API_KEY,
        "User-Agent": "job-hunt-assistant",
        "Host": "data.usajobs.gov",
        "Accept": "application/json",
    }

    params = {
        "Keyword": keyword,
        "LocationName": location,
        "ResultsPerPage": results_per_page,
    }

    last_error = None
    for attempt in range(3):
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get("SearchResult", {}).get("SearchResultItems", [])
        except RequestException as exc:
            last_error = exc
            if attempt < 2:
                sleep(2 ** attempt)
                continue
            raise ConnectionError(
                f"USAJobs API unreachable after 3 attempts: {exc.__class__.__name__}"
            ) from last_error
