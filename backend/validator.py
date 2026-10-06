from .scheduler import minutes

def validate_schedule(schedule, preferences, calendar_events):
    events = schedule.events
    for e in events:
        if minutes(e.start_time) >= minutes(e.end_time):
            return {"valid": False, "error": f"Invalid time range for '{e.activity}'."}
    ordered = sorted(events, key=lambda e: minutes(e.start_time))
    for a, b in zip(ordered, ordered[1:]):
        if minutes(b.start_time) < minutes(a.end_time):
            return {"valid": False, "error": f"Overlap between '{a.activity}' and '{b.activity}'."}
    wake, sleep = minutes(preferences["wake_time"]), minutes(preferences["sleep_time"])
    work_start, work_end = minutes(preferences["preferred_work_start"]), minutes(preferences["preferred_work_end"])
    for e in events:
        s, f = minutes(e.start_time), minutes(e.end_time)
        if s < wake or f > sleep:
            return {"valid": False, "error": f"'{e.activity}' is outside sleep boundaries."}
        if e.event_type == "work" and (s < work_start or f > work_end):
            return {"valid": False, "error": f"'{e.activity}' is outside preferred working hours."}
    for e in events:
        if e.event_type == "calendar":
            continue
        for fixed in calendar_events:
            if minutes(e.start_time) < minutes(fixed["end_time"]) and minutes(fixed["start_time"]) < minutes(e.end_time):
                return {"valid": False, "error": f"'{e.activity}' conflicts with '{fixed['title']}'."}
    return {"valid": True, "error": None}
