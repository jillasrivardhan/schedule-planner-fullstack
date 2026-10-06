from typing import List, Optional
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    deadline: Optional[str] = None
    duration: int = Field(gt=0, le=720)

class Preferences(BaseModel):
    wake_time: str = "06:00"
    sleep_time: str = "22:30"
    preferred_work_start: str = "08:00"
    preferred_work_end: str = "20:00"
    preferred_deep_work_time: str = "morning"
    break_duration: int = Field(default=15, ge=0, le=120)
    exercise_preference: str = "evening"

class ScheduleEvent(BaseModel):
    start_time: str
    end_time: str
    activity: str
    event_type: str
    priority: str = "none"
    reason: str = ""

class DailySchedule(BaseModel):
    date: str
    events: List[ScheduleEvent]
    planning_summary: str

class PlanRequest(BaseModel):
    date: str
    request: str = "Create the most productive realistic schedule for this day."

class ApprovalRequest(BaseModel):
    date: str
    schedule: DailySchedule
