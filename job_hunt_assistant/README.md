# Job Hunt Assistant

An AI-powered multi-agent job search assistant that helps users discover jobs, analyze job descriptions, and generate tailored application material such as resume summaries, cover letters, and outreach messages.

## What it does

This project combines live job search, LLM-based writing, application tracking, and analytics in one Streamlit application.

### Core capabilities

- Search live job listings from Adzuna
- Score how well a resume matches a job description
- Run a three-agent CrewAI workflow
- Generate tailored resume summaries
- Generate cover letters
- Generate recruiter outreach messages
- Detect duplicate applications
- Track applications in CSV and database form
- Visualize application analytics
- Fall back to SQLite if PostgreSQL is not available locally

## Tech Stack

- Frontend: Streamlit
- Orchestration: CrewAI
- LLM: Gemini
- Job API: Adzuna
- Database: PostgreSQL with SQLite fallback
- Persistence: SQLAlchemy
- Analytics: Streamlit + Plotly
- Testing: Pytest
- CI/CD: GitHub Actions
- Containerization: Docker and Docker Compose

## Project Structure

```text
job_hunt_assistant/
|-- agents/                # JD, resume, and messaging agents
|-- data/                  # logs, cache, generated cover letters
|-- models/                # SQLAlchemy database models
|-- pages/                 # Streamlit multipage screens
|-- scripts/               # one-off helper scripts
|-- services/              # matching, analytics, deduplication, LLM providers
|-- tests/                 # automated tests
|-- utils/                 # config, logging, API wrappers, tracking
|-- orchestrator.py        # main workflow runner
|-- streamlit_app.py       # main UI entry point
|-- Dockerfile             # container image
|-- docker-compose.yml     # local app + PostgreSQL
|-- PROJECT_REPORT.md      # detailed project explanation
|-- README.md              # this file
```

## Architecture

```mermaid
flowchart TD
    User --> UI[Streamlit UI]
    UI --> Config[Config Validation]
    UI --> API[Adzuna API]
    UI --> Score[Match Scoring]
    UI --> Dedup[Duplicate Detection]
    UI --> Crew[CrewAI Orchestrator]

    Crew --> JD[JD Analyst Agent]
    Crew --> Resume[Resume/CL Agent]
    Crew --> Msg[Messaging Agent]

    JD --> LLM[Gemini]
    Resume --> LLM
    Msg --> LLM

    Crew --> Track[Tracking Layer]
    Track --> CSV[CSV Log]
    Track --> DB[(SQLAlchemy DB)]

    DB --> Analytics[Analytics Dashboard]
    CSV --> History[Application History]
```

## File Roles

- `streamlit_app.py`: the user interface and main interaction flow
- `orchestrator.py`: creates tasks, runs agents, saves outputs
- `agents/`: specialized AI agents for the job workflow
- `utils/india_jobs_api.py`: Adzuna integration
- `utils/tracking.py`: CSV, cover letter, and database persistence
- `utils/config_validator.py`: startup checks for required keys
- `models/database.py`: SQLAlchemy tables and DB fallback
- `services/matching.py`: resume and job similarity scoring
- `services/deduplication.py`: duplicate detection logic
- `services/analytics.py`: dashboard metrics
- `pages/analytics_dashboard.py`: analytics UI page

## Requirements

- Python 3.10+
- Gemini API key
- Adzuna API ID and key
- PostgreSQL is optional for local development because SQLite fallback is built in

## Setup

### 1. Open the project

```powershell
cd "C:\Users\HP\OneDrive\Desktop\Multi-Agent Job Search System\job_hunt_assistant"
```

### 2. Activate the environment

```powershell
..\env\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit `utils/.env`:

```env
GEMINI_API_KEY=your_gemini_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
DATABASE_URL=postgresql://user:password@localhost:5432/job_hunt
LOG_LEVEL=INFO
```

If PostgreSQL is not running, the app will automatically use local SQLite.

## Run the app

```powershell
streamlit run streamlit_app.py
```

Then open the local URL Streamlit prints, usually:

```text
http://localhost:8501
```

## Initialize the database

Optional for local development:

```powershell
cd "C:\Users\HP\OneDrive\Desktop\Multi-Agent Job Search System"
..\env\Scripts\Activate.ps1
python scripts\init_db.py
```

## Run tests

```powershell
cd "C:\Users\HP\OneDrive\Desktop\Multi-Agent Job Search System"
..\env\Scripts\Activate.ps1
python -m pytest tests -q
```

## Docker

```powershell
cd "C:\Users\HP\OneDrive\Desktop\Multi-Agent Job Search System\job_hunt_assistant"
docker-compose up --build
```

## How the app works

1. Enter a role, location, resume text, and short bio.
2. The app fetches live jobs from Adzuna.
3. Each job is scored against the resume text.
4. Duplicate applications are skipped.
5. The CrewAI workflow generates tailored application content.
6. Outputs are saved to CSV, database, and cover letter files.
7. The analytics dashboard reads the stored data and shows metrics.

## Environment variables

- `GEMINI_API_KEY`: required for AI generation
- `ADZUNA_APP_ID`: required for job search
- `ADZUNA_APP_KEY`: required for job search
- `DATABASE_URL`: optional, defaults to SQLite fallback if PostgreSQL is unavailable
- `LOG_LEVEL`: optional logging level

## Testing

The test suite covers:

- Adzuna API parsing
- agent creation
- matching score logic
- duplicate detection
- analytics metrics
- configuration validation

## Troubleshooting

- If old CSV data causes issues, rename or delete `data/applications_log.csv`.
- If PostgreSQL is not running, the project will use SQLite automatically.
- If the app complains about missing keys, check `utils/.env`.

## Documentation

- [`PROJECT_REPORT.md`](PROJECT_REPORT.md): detailed project explanation and architecture

## License

MIT
