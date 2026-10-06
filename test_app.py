from backend.scheduler import minutes, hhmm, generate_schedule
from backend.validator import validate_schedule

def test_time_conversion():
    assert minutes("08:30") == 510
    assert hhmm(510) == "08:30"

def test_schedule_is_valid():
    preferences={"wake_time":"06:00","sleep_time":"22:30","preferred_work_start":"08:00","preferred_work_end":"20:00","preferred_deep_work_time":"morning","break_duration":15,"exercise_preference":"evening"}
    tasks=[{"title":"Important Task","priority":"high","deadline":"2026-10-07","duration":60}]
    calendar=[{"title":"College","start_time":"09:00","end_time":"12:00"}]
    schedule=generate_schedule("2026-10-06",tasks,preferences,calendar,["Important Task"])
    assert validate_schedule(schedule,preferences,calendar)["valid"] is True
