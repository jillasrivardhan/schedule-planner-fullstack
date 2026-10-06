from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db, seed_demo, get_tasks, add_task, delete_task, get_preferences, save_preferences, get_local_calendar, save_schedule
from .models import TaskCreate, Preferences, PlanRequest, ApprovalRequest
from .agent import run_agent
from .scheduler import generate_schedule
from .validator import validate_schedule
from .google_calendar import is_connected, get_authorization_url, complete_authorization, get_events as google_get_events, create_event as google_create_event
from .config import OLLAMA_MODEL

app = FastAPI(title="AI Daily Schedule Planner", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"

@app.on_event("startup")
def startup():
    init_db()
    seed_demo()

@app.get("/")
def home(): return FileResponse(FRONTEND / "index.html")

@app.get("/api/health")
def health(): return {"status": "ok", "service": "AI Daily Schedule Planner"}

@app.get("/api/state")
def state(): return {"google_calendar_connected": is_connected(), "ollama_model": OLLAMA_MODEL}

@app.get("/api/tasks")
def tasks(): return get_tasks()

@app.post("/api/tasks")
def create_task(data: TaskCreate): return {"id": add_task(data), **data.model_dump(), "status": "pending"}

@app.delete("/api/tasks/{task_id}")
def remove_task(task_id: int): delete_task(task_id); return {"ok": True}

@app.get("/api/preferences")
def preferences(): return get_preferences()

@app.put("/api/preferences")
def update_preferences(data: Preferences): save_preferences(data); return data

@app.get("/api/calendar/{target_date}")
def calendar(target_date: str):
    if is_connected(): return {"source": "google", "events": google_get_events(target_date)}
    return {"source": "local", "events": get_local_calendar(target_date)}

@app.get("/api/auth/google/status")
def google_status(): return {"connected": is_connected()}

@app.get("/api/auth/google")
def google_auth():
    try: return RedirectResponse(get_authorization_url()[0])
    except FileNotFoundError as exc: raise HTTPException(status_code=400, detail=str(exc))

@app.get("/api/auth/google/callback")
def google_callback(code: str):
    try:
        complete_authorization(code)
        return RedirectResponse("/")
    except Exception as exc: raise HTTPException(status_code=400, detail=f"Google authorization failed: {exc}")

@app.post("/api/plan")
def plan(request: PlanRequest):
    try:
        agent_result = run_agent(request.date, request.request)
        tasks_data = get_tasks()
        preferences_data = get_preferences()
        calendar_events = google_get_events(request.date) if is_connected() else get_local_calendar(request.date)
        schedule = generate_schedule(request.date, tasks_data, preferences_data, calendar_events, agent_result.get("priority_order", []))
        validation = validate_schedule(schedule, preferences_data, calendar_events)
        if not validation["valid"]: raise HTTPException(status_code=500, detail=validation["error"])
        return {"schedule": schedule.model_dump(), "validation": validation,
                "agent_reasoning": agent_result.get("planning_context", ""),
                "calendar_source": "google" if is_connected() else "local"}
    except HTTPException: raise
    except Exception as exc: raise HTTPException(status_code=500, detail=str(exc))

@app.post("/api/approve")
def approve(request: ApprovalRequest):
    preferences_data = get_preferences()
    calendar_events = google_get_events(request.date) if is_connected() else get_local_calendar(request.date)
    validation = validate_schedule(request.schedule, preferences_data, calendar_events)
    if not validation["valid"]: raise HTTPException(status_code=400, detail=validation["error"])
    created = []
    if is_connected():
        for event in request.schedule.events:
            if event.event_type != "calendar":
                result = google_create_event(request.date, event.start_time, event.end_time, event.activity, event.reason)
                created.append({"id": result.get("id"), "title": event.activity})
    save_schedule(request.date, request.schedule.model_dump(), "approved")
    return {"approved": True, "google_events_created": len(created), "created": created, "storage": "sqlite"}

@app.get("/app.js")
def app_js(): return FileResponse(FRONTEND / "app.js", media_type="application/javascript")

@app.get("/styles.css")
def styles_css(): return FileResponse(FRONTEND / "styles.css", media_type="text/css")
