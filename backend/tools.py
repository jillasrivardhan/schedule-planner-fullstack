from langchain_core.tools import tool
from .database import get_tasks, get_preferences, get_local_calendar
from .google_calendar import get_events as google_get_events, is_connected

@tool
def get_tasks_tool() -> str:
    """Get all pending tasks with priority, deadline and duration."""
    tasks = get_tasks()
    if not tasks:
        return "No pending tasks."
    return "\n".join(
        f"{t['title']} | priority={t['priority']} | duration={t['duration']}m | deadline={t['deadline'] or 'none'}"
        for t in tasks
    )

@tool
def get_preferences_tool() -> str:
    """Get the user's scheduling preferences."""
    p = get_preferences()
    if not p:
        return "No scheduling preferences found."
    return (f"wake={p['wake_time']} | sleep={p['sleep_time']} | work={p['preferred_work_start']}-{p['preferred_work_end']} | "
            f"deep_work={p['preferred_deep_work_time']} | break={p['break_duration']}m | exercise={p['exercise_preference']}")

@tool
def get_calendar_tool(date: str) -> str:
    """Get fixed calendar events for a specific YYYY-MM-DD date."""
    events = google_get_events(date) if is_connected() else get_local_calendar(date)
    if not events:
        return f"No calendar events on {date}."
    return "\n".join(f"{e['start_time']}-{e['end_time']} | {e['title']} | source={e['source']}" for e in events)
