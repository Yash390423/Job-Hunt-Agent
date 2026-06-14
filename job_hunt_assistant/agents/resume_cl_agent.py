try:
    from utils.config import GEMINI_API_KEY
except ImportError:  # pragma: no cover - fallback for package-style imports
    from job_hunt_assistant.utils.config import GEMINI_API_KEY

from pathlib import Path

from crewai import Agent, LLM, Task
from langchain_google_genai import ChatGoogleGenerativeAI


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=GEMINI_API_KEY,
)
crew_llm = LLM(model="gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY)
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "resume_agent_output.txt"


def get_resume_cl_agent():
    return Agent(
        role="Resume and Cover Letter Specialist",
        goal=(
            "Tailor resumes and write compelling, job-specific cover letters for "
            "government and public sector roles."
        ),
        backstory=(
            "You are an expert career writer who adapts candidate materials for "
            "government jobs with clarity, professionalism, and strong alignment "
            "to the job description."
        ),
        llm=crew_llm,
        verbose=True,
        allow_delegation=False,
    )


def create_resume_cl_task(agent, job_summary, resume_text):
    return Task(
        description=(
            "Using the job summary and candidate resume below, tailor the resume summary "
            "and write a personalized cover letter for a government job.\n\n"
            "Instructions:\n"
            "1. Rewrite the candidate's resume summary so it aligns with the role.\n"
            "2. Write a polished cover letter suitable for a government application.\n"
            "3. Use the exact output markers <<RESUME_SUMMARY>> and <<COVER_LETTER>>.\n"
            "4. Keep the tone professional, specific, and concise.\n\n"
            f"Job Summary:\n{job_summary}\n\n"
            f"Resume Text:\n{resume_text}"
        ),
        expected_output=(
            "A markdown-free plain text response that includes the exact markers "
            "<<RESUME_SUMMARY>> and <<COVER_LETTER>>, followed by the tailored resume "
            "summary and the personalized cover letter."
        ),
        agent=agent,
        output_file=str(OUTPUT_PATH),
    )
