try:
    from utils.config import GEMINI_API_KEY
except ImportError:  # pragma: no cover - fallback for package-style imports
    from job_hunt_assistant.utils.config import GEMINI_API_KEY

from pathlib import Path

from crewai import Agent, LLM, Task
from langchain_google_genai import ChatGoogleGenerativeAI


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
)
crew_llm = LLM(model="gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY)


def get_messaging_agent():
    return Agent(
        role="Outreach Message Writer",
        goal=(
            "Write short, personalized outreach messages that help job seekers "
            "connect with hiring managers and recruiters."
        ),
        backstory=(
            "You are a concise and persuasive career communicator who writes "
            "professional LinkedIn and email outreach tailored to each role."
        ),
        llm=crew_llm,
        verbose=True,
        allow_delegation=False,
    )


def create_messaging_task(agent, job_summary, agency_name, user_bio):
    return Task(
        description=(
            "Write a brief, professional outreach message expressing interest in the job.\n\n"
            "Use the job summary, agency name, and user bio to personalize the message.\n"
            "Make it suitable for LinkedIn or email, and keep it warm, confident, and concise.\n\n"
            f"Agency Name:\n{agency_name}\n\n"
            f"Job Summary:\n{job_summary}\n\n"
            f"User Bio:\n{user_bio}"
        ),
        expected_output=(
            "A polished outreach message under 150 words that is tailored for LinkedIn "
            "or email, shows genuine interest, and highlights relevant background without "
            "being overly long."
        ),
        agent=agent,
    )
