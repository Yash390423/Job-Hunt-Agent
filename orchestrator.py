import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from agents.jd_analyst import create_jd_analysis_task, get_jd_analyst_agent
    from agents.messaging_agent import create_messaging_task, get_messaging_agent
    from agents.resume_cl_agent import create_resume_cl_task, get_resume_cl_agent
    from utils.india_jobs_api import fetch_india_jobs
    from utils.tracking import log_application, save_cover_letter_file
except ImportError:  # pragma: no cover - fallback for package-style imports
    from job_hunt_assistant.agents.jd_analyst import (
        create_jd_analysis_task,
        get_jd_analyst_agent,
    )
    from job_hunt_assistant.agents.messaging_agent import (
        create_messaging_task,
        get_messaging_agent,
    )
    from job_hunt_assistant.agents.resume_cl_agent import (
        create_resume_cl_task,
        get_resume_cl_agent,
    )
    from job_hunt_assistant.utils.india_jobs_api import fetch_india_jobs
    from job_hunt_assistant.utils.tracking import (
        log_application,
        save_cover_letter_file,
    )

from crewai import Crew, Process

CACHE_PATH = Path(__file__).resolve().parent / "data" / "india_jobs_cache.json"
JOB_SEARCH_KEYWORD = "business analyst"
JOB_LOCATION = "India"
USER_BIO = "I'm a data professional passionate about public service."


def _extract_job_summary(job_post):
    descriptor = job_post.get("MatchedObjectDescriptor", {})
    if not descriptor:
        descriptor = job_post

    title = descriptor.get("PositionTitle", "Unknown Title")
    organization = descriptor.get("OrganizationName", "Unknown Organization")
    location_data = descriptor.get("PositionLocation", [])
    locations = ", ".join(loc.get("LocationName", "") for loc in location_data if loc.get("LocationName"))
    summary_parts = [
        f"Title: {title}",
        f"Organization: {organization}",
    ]
    if locations:
        summary_parts.append(f"Location: {locations}")

    for field_name in ("PositionFormattedDescription", "QualificationSummary"):
        field_value = descriptor.get(field_name)
        if field_value:
            summary_parts.append(f"{field_name}:\n{field_value}")

    return "\n\n".join(summary_parts)


def _extract_job_metadata(job_post):
    descriptor = job_post.get("MatchedObjectDescriptor", {})
    if not descriptor:
        descriptor = job_post

    agency_name = descriptor.get("OrganizationName", "Unknown Organization")
    job_title = descriptor.get("PositionTitle", "Unknown Title")
    return agency_name, job_title


def load_resume():
    resume_path = Path(__file__).resolve().parent / "data" / "sample_resume.txt"
    return resume_path.read_text(encoding="utf-8")


def _save_cached_job_post(job_post):
    CACHE_PATH.write_text(json.dumps(job_post, indent=2), encoding="utf-8")


def _load_cached_job_post():
    if not CACHE_PATH.exists():
        return None
    return json.loads(CACHE_PATH.read_text(encoding="utf-8"))


def _short_error(exc):
    message = str(exc).strip().replace("\n", " ")
    if len(message) > 180:
        message = message[:177] + "..."
    return message


def extract_between_markers(text, start_marker, end_marker):
    start_index = text.find(start_marker)
    if start_index == -1:
        return ""

    start_index += len(start_marker)
    if not end_marker:
        return text[start_index:].strip()

    end_index = text.find(end_marker, start_index)
    if end_index == -1:
        return text[start_index:].strip()

    return text[start_index:end_index].strip()


def _get_job_post(keyword=JOB_SEARCH_KEYWORD, location=JOB_LOCATION):
    try:
        job_posts = fetch_india_jobs(keyword, location)
        if job_posts:
            first_job = job_posts[0]
            _save_cached_job_post(first_job)
            return first_job
        print("[IndiaJobs] returned no results; trying the last cached India job post.")
    except Exception as exc:
        print(f"[IndiaJobs] lookup failed: {_short_error(exc)}")
        print("[IndiaJobs] trying the last cached India job post.")

    cached_job = _load_cached_job_post()
    if cached_job is not None:
        return cached_job

    raise RuntimeError(
        "India job source is currently unavailable and no cached posting exists yet."
    )


def run_pipeline(job_data, resume_text, user_bio):
    job_summary = _extract_job_summary(job_data)
    agency_name, job_title = _extract_job_metadata(job_data)

    jd_analyst_agent = get_jd_analyst_agent()
    resume_writer_agent = get_resume_cl_agent()
    messaging_agent = get_messaging_agent()
    analysis_task = create_jd_analysis_task(jd_analyst_agent, job_summary)
    resume_task = create_resume_cl_task(resume_writer_agent, job_summary, resume_text)
    messaging_task = create_messaging_task(
        messaging_agent,
        job_summary,
        agency_name,
        user_bio,
    )

    crew = Crew(
        agents=[jd_analyst_agent, resume_writer_agent, messaging_agent],
        tasks=[analysis_task, resume_task, messaging_task],
        process=Process.sequential,
        verbose=True,
    )

    try:
        result = crew.kickoff()
    except Exception as exc:
        message = f"[Gemini/Crew] failed: {_short_error(exc)}"
        print(message)
        return message

    resume_agent_output = str(resume_task.output)
    resume_summary = extract_between_markers(
        resume_agent_output,
        "<<RESUME_SUMMARY>>",
        "<<COVER_LETTER>>",
    )
    cover_letter = extract_between_markers(
        resume_agent_output,
        "<<COVER_LETTER>>",
        "",
    )

    if resume_summary:
        log_application(job_title, agency_name, resume_summary)
    if cover_letter:
        save_cover_letter_file(job_title, cover_letter)

    print(result)
    return str(result)


if __name__ == "__main__":
    try:
        first_job = _get_job_post()
        resume_text = load_resume()
        print(run_pipeline(first_job, resume_text, USER_BIO))
    except Exception as exc:
        print(f"[IndiaJobs] fatal: {_short_error(exc)}")
