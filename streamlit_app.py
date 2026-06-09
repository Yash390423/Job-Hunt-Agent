import streamlit as st

from orchestrator import run_pipeline
from usajobs_api import fetch_usajobs


st.title("Job Hunt Assistant")
st.markdown(
    "Search live USAJobs postings, choose one or more roles, and run the agent "
    "workflow to generate tailored application materials."
)

keyword = st.text_input("Job keyword", value="data scientist")
location = st.text_input("Location", value="remote")
resume_text = st.text_area(
    "Resume text",
    value="Paste your resume here...",
    height=220,
)
bio = st.text_area(
    "Bio",
    value="I'm a data professional passionate about public service.",
    height=120,
)

if "job_posts" not in st.session_state:
    st.session_state.job_posts = []

if "job_results" not in st.session_state:
    st.session_state.job_results = {}

if st.button("Run Job Hunt Assistant"):
    with st.spinner("Fetching USAJobs listings..."):
        st.session_state.job_posts = fetch_usajobs(keyword, location, results_per_page=5)
        st.session_state.job_results = {}

if st.session_state.job_posts:
    st.markdown("### Select Jobs")
    for index, job_post in enumerate(st.session_state.job_posts):
        descriptor = job_post.get("MatchedObjectDescriptor", {})
        title = descriptor.get("PositionTitle", "Unknown Title")
        agency = descriptor.get("OrganizationName", "Unknown Organization")
        st.checkbox(
            f"{title} - {agency}",
            key=f"job_select_{index}",
        )

    if st.button("Apply to Selected Job"):
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

                with st.spinner(f"Running workflow for {title}..."):
                    result = run_pipeline(job_post, resume_text, bio)
                    st.session_state.job_results[index] = result

    if st.session_state.job_results:
        st.markdown("### Results")
        for index, job_post in enumerate(st.session_state.job_posts):
            if index in st.session_state.job_results:
                descriptor = job_post.get("MatchedObjectDescriptor", {})
                title = descriptor.get("PositionTitle", "Unknown Title")
                agency = descriptor.get("OrganizationName", "Unknown Organization")
                st.markdown(f"#### {title} - {agency}")
                st.markdown(st.session_state.job_results[index])
