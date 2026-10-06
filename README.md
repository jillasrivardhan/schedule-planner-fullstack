# AI Daily Schedule Planner

> A full-stack AI-powered daily scheduling application that combines a **LangGraph single agent**, **tool calling**, **Google Calendar**, and a **deterministic Python scheduling engine**.

The core design principle is simple:

**The LLM reasons about priorities. Python handles exact time.**

This prevents common LLM scheduling failures such as invalid time ranges, overlapping events, and schedules outside working or sleeping hours.

---

## ✨ Project Overview

The AI Daily Schedule Planner helps a user turn pending tasks, personal scheduling preferences, and existing calendar commitments into a realistic daily schedule.

The application:

1. Understands the user's scheduling request.
2. Uses an agent to gather planning information through tools.
3. Lets the LLM reason about task priority.
4. Uses a deterministic Python scheduling engine to calculate exact time slots.
5. Validates the generated schedule.
6. Shows the schedule to the user for approval.
7. Saves the approved schedule.
8. Creates Google Calendar events when Google Calendar is connected.

If Google Calendar is not configured, the application automatically runs with a local SQLite demo calendar.

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      User / Browser  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    HTML/CSS/JS UI   │
                         └──────────┬───────────┘
                                    │ REST API
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   LangGraph Agent    │
                         │    (single agent)    │
                         └──────────┬───────────┘
                                    │
                       ┌────────────┼────────────┐
                       │            │            │
                       ▼            ▼            ▼
                 Tasks Tool   Preferences   Calendar Tool
                                      Tool          │
                                                    │
                                  ┌─────────────────┴──────────────┐
                                  │                                │
                                  ▼                                ▼
                           SQLite Demo Calendar            Google Calendar
                                  │                         (optional OAuth)
                                  └─────────────────┬──────────────┘
                                                    ▼
                                     ┌────────────────────────┐
                                     │ Priority / Planning    │
                                     │ decision from the LLM  │
                                     └────────────┬───────────┘
                                                  ▼
                                     ┌────────────────────────┐
                                     │ Deterministic Python    │
                                     │ Scheduling Engine       │
                                     └────────────┬───────────┘
                                                  ▼
                                     ┌────────────────────────┐
                                     │ Deterministic Validator │
                                     └────────────┬───────────┘
                                                  ▼
                                     ┌────────────────────────┐
                                     │ User Approval           │
                                     └────────────┬───────────┘
                                                  ▼
                                  ┌──────────────────────────────┐
                                  │ SQLite + Google Calendar     │
                                  └──────────────────────────────┘
```

### Why use a deterministic scheduler?

An LLM is useful for understanding natural language and making prioritization decisions, but it should not be trusted with exact scheduling arithmetic.

For example, Python handles:

- `09:00 + 120 minutes = 11:00`
- overlap detection
- available-slot calculation
- sleep boundaries
- preferred working hours
- task duration
- calendar conflicts
- final validation

This separation makes the application more reliable and easier to debug.

---

## 🧰 Technology Stack

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript

### Backend

- Python
- FastAPI
- Uvicorn

### AI / Agent

- LangChain
- LangGraph
- Ollama
- Qwen2.5:3B by default

### Data

- SQLite
- Pydantic

### Calendar

- Google Calendar API
- Google OAuth 2.0

---

## 📁 Project Structure

```text
schedule-planner-fullstack/
│
├── backend/
│   ├── __init__.py
│   ├── agent.py              # LangGraph single-agent workflow
│   ├── config.py             # Environment/configuration
│   ├── database.py           # SQLite operations and demo seed data
│   ├── google_calendar.py    # Google OAuth + Calendar API
│   ├── main.py               # FastAPI application and REST endpoints
│   ├── models.py             # Pydantic models
│   ├── scheduler.py          # Deterministic scheduling engine
│   ├── tools.py              # Agent tools
│   └── validator.py          # Deterministic schedule validation
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── data/
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── requirements.txt
├── test_app.py
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites

Install:

- Python 3.11+
- Ollama
- Git

Python 3.12 is recommended for this project.

---

### 2. Clone the repository

```bash
git clone https://github.com/<your-username>/schedule-planner-fullstack.git
cd schedule-planner-fullstack
```

---

### 3. Create a virtual environment

#### Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
```

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Install and start Ollama

Install Ollama and pull the default model:

```bash
ollama pull qwen2.5:3b
```

Start Ollama:

```bash
ollama serve
```

Keep Ollama running while using the application.

The model can be changed through `.env`.

---

### 6. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

The default configuration is:

```env
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_BASE_URL=http://localhost:11434
APP_HOST=127.0.0.1
APP_PORT=8000

GOOGLE_CLIENT_SECRETS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/api/auth/google/callback
```

**Never commit `.env`, `credentials.json`, or `token.json`.**

---

## ▶️ Run the Application

Start FastAPI:

```bash
uvicorn backend.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The application should load the full-stack web interface.

---

# 📅 Google Calendar Integration

Google Calendar is optional.

The application works without Google OAuth by using a local SQLite demo calendar.

To enable Google Calendar, each person using the application should configure **their own Google Cloud OAuth credentials**.

## Google Cloud Setup

1. Open Google Cloud Console.
2. Create or select a Google Cloud project.
3. Enable the **Google Calendar API**.
4. Configure the Google OAuth consent screen.
5. Create an OAuth client.
6. Add the following redirect URI:

```text
http://127.0.0.1:8000/api/auth/google/callback
```

7. Download the OAuth client JSON.
8. Rename it:

```text
credentials.json
```

9. Place it in the project root:

```text
schedule-planner-fullstack/
└── credentials.json
```

10. Start the application and click:

**Connect Google Calendar**

The OAuth token will be stored locally as:

```text
token.json
```

Both files are excluded by `.gitignore`.

### Important

Do not upload your own:

- `credentials.json`
- `token.json`
- `.env`

to GitHub.

For project submission, distribute the source code and let the evaluator configure their own Google Cloud OAuth application.

---

# 🧠 Agent Workflow

The LangGraph agent is intentionally kept focused.

```text
User request
     ↓
LangGraph Agent
     ↓
Get pending tasks
     ↓
Get scheduling preferences
     ↓
Get calendar events
     ↓
Reason about priorities
     ↓
Return priority order
     ↓
Python Scheduling Engine
```

The agent does **not** calculate the final clock times.

This keeps the LLM responsible for reasoning while Python remains responsible for deterministic scheduling.

---

# 🛠️ Available Agent Tools

### Task Tool

Retrieves pending tasks including:

- title
- priority
- duration
- deadline

### Preference Tool

Retrieves:

- wake time
- sleep time
- preferred working hours
- preferred deep-work period
- break duration
- exercise preference

### Calendar Tool

Retrieves fixed events for the requested date.

The source is:

- Google Calendar when connected
- local SQLite demo calendar otherwise

---

# 📊 Scheduling Engine

The deterministic scheduler:

- preserves fixed calendar events
- prioritizes tasks using the agent's priority decision
- considers task priority and deadlines
- respects working hours
- respects sleep boundaries
- respects task duration
- inserts breaks
- attempts to schedule exercise
- avoids overlaps
- reports tasks that could not fit

If all tasks cannot fit, the application does not force them into invalid time ranges.

Instead, it reports the tasks that could not be scheduled.

---

# ✅ Validation

Before a schedule reaches the user as a valid schedule, Python checks:

### Time validity

```text
start < end
```

### Overlap

```text
Event A does not overlap Event B
```

### Sleep boundaries

```text
wake_time <= event <= sleep_time
```

### Working hours

Work tasks must stay within the preferred working period.

### Calendar conflicts

Generated events cannot overlap fixed calendar commitments.

---

# 💾 Database

SQLite is used for local persistence.

The application stores:

- tasks
- scheduling preferences
- local demo calendar events
- approved schedules

The database is generated automatically in:

```text
data/schedule.db
```

Database files are ignored by Git.

---

# 🧪 Testing

Run:

```bash
python -m pytest -q
```

The test suite checks core scheduling behavior such as time conversion and schedule validation.

You can also run Python's compiler check:

```bash
python -m compileall -q backend
```

---

# 🔌 REST API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/state` | Application/Google Calendar state |
| GET | `/api/tasks` | Get pending tasks |
| POST | `/api/tasks` | Add a task |
| DELETE | `/api/tasks/{task_id}` | Delete a task |
| GET | `/api/preferences` | Get preferences |
| PUT | `/api/preferences` | Update preferences |
| GET | `/api/calendar/{date}` | Get calendar events |
| GET | `/api/auth/google` | Start Google OAuth |
| GET | `/api/auth/google/callback` | OAuth callback |
| GET | `/api/auth/google/status` | Check Google connection |
| POST | `/api/plan` | Generate and validate a schedule |
| POST | `/api/approve` | Approve/save schedule and create Google events |

FastAPI also provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

# 🎯 Example User Requests

Try requests such as:

```text
Create the most productive realistic schedule for tomorrow.
```

```text
Prioritize my urgent tasks and respect my existing calendar.
```

```text
Plan my day around my college schedule and include breaks.
```

```text
Prioritize tasks with the closest deadlines.
```

```text
Schedule difficult work during my preferred deep-work period.
```

```text
Don't overload my day. If everything cannot fit, prioritize the most important tasks.
```

---

# 🔐 Security Notes

This repository intentionally does **not** contain personal Google credentials.

The following files must remain local:

```text
.env
credentials.json
token.json
data/*.db
```

They are already included in `.gitignore`.

If an API key, OAuth secret, or token is accidentally committed, remove it from Git history and revoke/rotate the exposed credential.

---

# 🧩 Design Decisions

### Why LangGraph?

LangGraph provides explicit graph/state-based agent workflows and makes the tool-calling flow easier to extend.

### Why Ollama?

Ollama allows the application to run an LLM locally without requiring a paid model API key.

### Why not let the LLM generate the final schedule directly?

Because exact time arithmetic and constraint checking are deterministic problems.

The architecture therefore separates:

```text
LLM
→ reasoning
→ prioritization
→ tool usage

Python
→ time arithmetic
→ slot generation
→ conflict detection
→ validation
```

### Why Google Calendar?

It provides real-world calendar context and allows approved schedule events to become actual calendar events.

---

# 🔮 Future Improvements

Potential extensions include:

- Google Calendar event update/delete support
- recurring tasks
- multiple calendars
- timezone selection
- smarter deadline scoring
- automatic rescheduling
- APScheduler reminders
- authentication for multiple application users
- deployment with Docker
- production database such as PostgreSQL
- richer agent state and replanning
- mobile-friendly/PWA interface

---

# 📌 Project Status

**Current status: Working full-stack prototype**

Implemented:

- [x] FastAPI backend
- [x] Browser frontend
- [x] LangGraph single agent
- [x] LangChain tool calling
- [x] Task management
- [x] Preference management API
- [x] Local SQLite calendar
- [x] Google Calendar OAuth integration
- [x] Google Calendar event retrieval
- [x] Google Calendar event creation
- [x] Deterministic scheduling engine
- [x] Deterministic validator
- [x] User approval flow
- [x] SQLite schedule persistence
- [x] Basic automated tests

---

## 👨‍💻 Author

**Sri Vardhan Jilla**

B.Tech — Computer Science and Engineering

Interested in:

- Artificial Intelligence
- Generative AI
- Agentic AI
- RAG
- LangChain
- LangGraph
- AI-powered applications

---

## 📄 License

This project is intended for educational, portfolio, and internship/project demonstration purposes.
