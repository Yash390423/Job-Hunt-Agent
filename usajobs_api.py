"""Legacy compatibility wrapper.

This project now uses India job listings via Adzuna, but this module is kept
so older imports do not break immediately.
"""

from utils.india_jobs_api import fetch_india_jobs as fetch_usajobs
