"""Legacy compatibility wrapper.

The project now fetches India job listings via Adzuna.
This module stays in place so any old imports keep working.
"""

from .india_jobs_api import fetch_india_jobs as fetch_usajobs
