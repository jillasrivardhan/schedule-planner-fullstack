# AI Daily Schedule Planner — Full Stack

Architecture:

Browser → FastAPI → LangGraph single agent → tool calling (tasks/preferences/Google Calendar) → deterministic Python scheduler → validator → user approval → SQLite + Google Calendar.

The LLM does understanding, tool selection and prioritization. Python does exact time arithmetic, slot generation, conflict detection and validation.

## Stack
FastAPI, vanilla HTML/CSS/JS, LangGraph, LangChain, Ollama, SQLite, Google Calendar API, Pydantic.

## Run
1. Install Python 3.11+ and Ollama.
2. `ollama pull qwen2.5:3b`
3. `ollama serve`
4. Create/activate a venv.
5. `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` (no OpenAI key required).
7. `uvicorn backend.main:app --reload`
8. Open http://127.0.0.1:8000

## Google Calendar
The app works in local demo mode without Google credentials. To connect Google Calendar, enable Google Calendar API in Google Cloud, create OAuth credentials, download the client JSON as `credentials.json`, place it in the project root, and add `http://127.0.0.1:8000/api/auth/google/callback` as an authorized redirect URI. Then click Connect Google Calendar.

The app reads Google events before planning and creates approved generated events after approval. `credentials.json` and `token.json` are ignored by Git.

## Demo data
The first run seeds tasks/preferences and three local events on 2026-10-06. Delete/edit the database if you want a fresh seed.

## Tests
`python -m pytest -q`
