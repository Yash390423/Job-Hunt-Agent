from pathlib import Path
import sys

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestrator import run_pipeline
from services.deduplication import check_duplicate
from services.matching import calculate_match_score
from utils.config_validator import validate_config
from utils.india_jobs_api import fetch_india_jobs
from utils.tracking import load_application_history


st.set_page_config(
    page_title="Job Hunt Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(59, 130, 246, 0.16), transparent 26%),
                radial-gradient(circle at top right, rgba(16, 185, 129, 0.12), transparent 24%),
                linear-gradient(180deg, #0b1120 0%, #111827 100%);
            color: #e5e7eb;
        }
        .hero-card {
            padding: 1.6rem 1.5rem;
            border-radius: 1.4rem;
            background: rgba(17, 24, 39, 0.82);
            border: 1px solid rgba(148, 163, 184, 0.18);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
        }
        .section-label {
            font-size: 0.8rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #93c5fd;
            margin-bottom: 0.35rem;
        }
        .job-card {
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 1rem;
            padding: 1rem 1rem 0.75rem 1rem;
            background: rgba(17, 24, 39, 0.78);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
            margin-bottom: 0.8rem;
        }
        .metric-chip {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.16);
            color: #dbeafe;
            font-size: 0.82rem;
            margin-right: 0.45rem;
            margin-bottom: 0.35rem;
            font-weight: 600;
        }
        .subtle-note {
            color: #cbd5e1;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


try:
    validate_config()
except ValueError as exc:
    st.error(str(exc))
    st.stop()


if "job_posts" not in st.session_state:
    st.session_state.job_posts = []

if "job_results" not in st.session_state:
    st.session_state.job_results = {}

if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = "data analyst"

if "search_location" not in st.session_state:
    st.session_state.search_location = "India"

if "last_search_count" not in st.session_state:
    st.session_state.last_search_count = 0

if "last_duplicates_skipped" not in st.session_state:
    st.session_state.last_duplicates_skipped = 0

st.sidebar.markdown("### Navigation")
st.sidebar.write("Search jobs, review matches, and generate application material.")
st.sidebar.markdown("### What this app does")
st.sidebar.markdown(
    """
    - Searches live job postings
    - Scores job matches against your resume
    - Skips duplicates
    - Generates application content
    - Stores results for analytics
    """
)
st.sidebar.markdown("### Tips")
st.sidebar.info("Paste a real resume to get more useful match scores and tailored outputs.")

st.markdown(
    """
    <div class="hero-card">
        <div class="section-label">AI Job Search Platform</div>
        <h1 style="margin-bottom:0.35rem;">Job Hunt Assistant</h1>
        <p class="subtle-note" style="margin-bottom:0.9rem;">
            Search live jobs, rank them against your resume, and generate tailored summaries,
            cover letters, and outreach messages in one flow.
        </p>
        <span class="metric-chip">Adzuna job search</span>
        <span class="metric-chip">Resume matching</span>
        <span class="metric-chip">Application tracking</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

col1, col2, col3 = st.columns(3)
col1.metric("Search keyword", st.session_state.search_keyword)
col2.metric("Location", st.session_state.search_location)
col3.metric("Jobs loaded", st.session_state.last_search_count)

st.write("")

with st.container():
    st.markdown("### Search Jobs")
    st.caption("Enter a role, location, resume text, and short bio to generate tailored application material.")

    with st.form("job_search_form"):
        keyword = st.text_input(
            "Job role or keyword",
            value=st.session_state.search_keyword,
            help="Examples: data analyst, software engineer, product manager",
        )
        location = st.text_input(
            "Location",
            value=st.session_state.search_location,
            help="Examples: India, Bengaluru, remote, Mumbai",
        )
        resume_text = st.text_area(
            "Resume text",
            value="Paste your resume here...",
            height=220,
            help="Use your actual resume text to get better match scoring and tailoring.",
        )
        bio = st.text_area(
            "Short bio",
            value="I'm a data professional passionate about public service.",
            height=120,
            help="A concise professional bio helps the outreach message feel more personal.",
        )
        search_clicked = st.form_submit_button("Search Jobs", use_container_width=True)


if search_clicked:
    st.session_state.search_keyword = keyword
    st.session_state.search_location = location
    with st.spinner("Fetching job listings..."):
        st.session_state.job_posts = fetch_india_jobs(
            keyword,
            location,
            results_per_page=5,
        )
        st.session_state.job_results = {}
        st.session_state.last_search_count = len(st.session_state.job_posts)
        st.session_state.last_duplicates_skipped = 0
        for index in range(len(st.session_state.job_posts)):
            st.session_state.pop(f"job_select_{index}", None)


if st.session_state.job_posts:
    existing_applications = load_application_history()
    duplicates_skipped = 0

    st.markdown("### Job Results")
    st.caption("Review the returned jobs, compare fit scores, and select the ones you want to process.")

    for index, job_post in enumerate(st.session_state.job_posts):
        descriptor = job_post.get("MatchedObjectDescriptor", {})
        title = descriptor.get("PositionTitle", "Unknown Title")
        agency = descriptor.get("OrganizationName", "Unknown Organization")
        location_items = descriptor.get("PositionLocation", [])
        location_text = ", ".join(
            loc.get("LocationName", "") for loc in location_items if loc.get("LocationName")
        ) or "Location not specified"
        job_description = (
            descriptor.get("PositionFormattedDescription")
            or descriptor.get("QualificationSummary")
            or ""
        )
        match_score = 0.0
        if resume_text and "Paste your resume here..." not in resume_text:
            match_score = calculate_match_score(resume_text, job_description)

        salary_hint = descriptor.get("Remuneration") or descriptor.get("Salary") or "Not listed"
        job_url = descriptor.get("PositionURI") or job_post.get("raw", {}).get("redirect_url", "")

        duplicate = check_duplicate(existing_applications, title, agency)
        card_label = f"{index + 1}. {title} - {agency}"

        with st.container():
            st.markdown('<div class="job-card">', unsafe_allow_html=True)
            top_left, top_right = st.columns([4, 1])
            with top_left:
                st.subheader(card_label)
                st.caption(location_text)
            with top_right:
                st.metric("Match", f"{match_score:.0f}%")

            st.markdown(
                f"""
                <div>
                    <span class="metric-chip">Company: {agency}</span>
                    <span class="metric-chip">Location: {location_text}</span>
                    <span class="metric-chip">Salary: {salary_hint}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            preview_text = job_description[:420].strip()
            if preview_text:
                st.write(preview_text + ("..." if len(job_description) > 420 else ""))
            else:
                st.write("No description preview available.")

            if job_url:
                st.link_button("Open job listing", job_url, use_container_width=False)

            if duplicate:
                st.warning("Already applied according to local history.")
            st.checkbox(
                "Select this job",
                key=f"job_select_{index}",
                disabled=duplicate,
            )
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Generate Application Material", use_container_width=True):
        selected_jobs = []
        for index, job_post in enumerate(st.session_state.job_posts):
            if st.session_state.get(f"job_select_{index}"):
                selected_jobs.append((index, job_post))

        if not selected_jobs:
            st.warning("Please select at least one job.")
        else:
            for index, job_post in selected_jobs:
                descriptor = job_post.get("MatchedObjectDescriptor", {})
                title = descriptor.get("PositionTitle", "Unknown Title")
                agency = descriptor.get("OrganizationName", "Unknown Organization")
                job_description = (
                    descriptor.get("PositionFormattedDescription")
                    or descriptor.get("QualificationSummary")
                    or ""
                )

                match_score = None
                if resume_text and "Paste your resume here..." not in resume_text:
                    match_score = calculate_match_score(resume_text, job_description)

                if check_duplicate(existing_applications, title, agency):
                    duplicates_skipped += 1
                    st.info(f"Skipping duplicate application for {title} at {agency}.")
                    continue

                with st.spinner(f"Generating material for {title}..."):
                    result = run_pipeline(job_post, resume_text, bio, match_score=match_score)
                    st.session_state.job_results[index] = result
                    existing_applications.append(
                        {
                            "job_title": title,
                            "company": agency,
                        }
                    )

            st.session_state.last_duplicates_skipped = duplicates_skipped

    if st.session_state.job_results:
        st.markdown("### Generated Results")
        st.caption("Each result below is the generated output for the selected job.")

        for index, job_post in enumerate(st.session_state.job_posts):
            if index in st.session_state.job_results:
                descriptor = job_post.get("MatchedObjectDescriptor", {})
                title = descriptor.get("PositionTitle", "Unknown Title")
                agency = descriptor.get("OrganizationName", "Unknown Organization")
                location_items = descriptor.get("PositionLocation", [])
                location_text = ", ".join(
                    loc.get("LocationName", "") for loc in location_items if loc.get("LocationName")
                ) or "Location not specified"
                job_url = descriptor.get("PositionURI") or job_post.get("raw", {}).get("redirect_url", "")
                job_description = (
                    descriptor.get("PositionFormattedDescription")
                    or descriptor.get("QualificationSummary")
                    or ""
                )
                result_text = st.session_state.job_results[index]
                score = 0.0
                if resume_text and "Paste your resume here..." not in resume_text:
                    score = calculate_match_score(resume_text, job_description)

                with st.expander(f"{title} - {agency}", expanded=True):
                    left, right = st.columns([3, 1])
                    with left:
                        st.write(f"**Location:** {location_text}")
                        st.write(f"**Job URL:** {job_url or 'Not available'}")
                        st.write(f"**Match score:** {score:.0f}%")
                    with right:
                        st.metric("Status", "Generated")
                    st.markdown(result_text)
