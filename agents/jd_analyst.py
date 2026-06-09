try:
    from utils.config import GEMINI_API_KEY
except ImportError:  # pragma: no cover - fallback for package-style imports
    from job_hunt_assistant.utils.config import GEMINI_API_KEY

from pathlib import Path

from crewai import Agent, LLM, Task
from langchain_google_genai import ChatGoogleGenerativeAI


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", google_api_key=GEMINI_API_KEY)
crew_llm = LLM(model="gemini/gemini-2.5-flash-lite", api_key=GEMINI_API_KEY)
REPORT_PATH = Path(__file__).resolve().parents[1] / "data" / "report.md"


def get_jd_analyst_agent():
    return Agent(
        role="Job Description Analyst",
        goal="Summarize job descriptions and extract the most important hiring details.",
        backstory=(
            "You are a detail-oriented recruiting analyst who turns long job posts "
            "into concise, structured hiring insights."
        ),
        llm=crew_llm,
        verbose=True,
        allow_delegation=False,
    )


def create_jd_analysis_task(agent, job_description):
    return Task(
        description=(
            "Analyze the following job description and extract the key details recruiters "
            "and job seekers would care about.\n\n"
            f"Job Description:\n{job_description}"
        ),
        expected_output=(
            "A markdown report with these sections:\n"
            "## Job Summary\n"
            "## Key Responsibilities\n"
            "## Required Skills\n"
            "## Qualifications\n"
            "## Preferred Experience\n"
            "## Application Notes\n"
            "Use short bullet points where appropriate and keep the writing clear and practical."
        ),
        agent=agent,
        output_file=str(REPORT_PATH),
    )
