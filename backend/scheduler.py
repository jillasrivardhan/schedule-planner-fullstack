from .models import DailySchedule, ScheduleEvent

def minutes(value):
    h, m = map(int, value.split(":"))
    return h * 60 + m

def hhmm(value):
    return f"{value // 60:02d}:{value % 60:02d}"

def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end

def choose_priority(tasks, priority_order):
    rank = {name.strip(): i for i, name in enumerate(priority_order)}
    pr = {"high": 0, "medium": 1, "low": 2}
    return sorted(tasks, key=lambda t: (rank.get(t["title"], 999), pr.get(t["priority"], 3), t["deadline"] or "9999-99-99"))

def free_slots(start, end, fixed, minimum=15):
    blocked = sorted((minutes(e["start_time"]), minutes(e["end_time"])) for e in fixed)
    slots, cursor = [], minutes(start)
    end_min = minutes(end)
    for b_start, b_end in blocked:
        if b_start > cursor and b_start - cursor >= minimum:
            slots.append((cursor, min(b_start, end_min)))
        cursor = max(cursor, b_end)
        if cursor >= end_min:
            break
    if cursor < end_min and end_min - cursor >= minimum:
        slots.append((cursor, end_min))
    return slots

def generate_schedule(date, tasks, preferences, fixed_events, priority_order):
    wake = minutes(preferences["wake_time"])
    sleep = minutes(preferences["sleep_time"])
    work_start = max(wake, minutes(preferences["preferred_work_start"]))
    work_end = min(sleep, minutes(preferences["preferred_work_end"]))
    break_duration = int(preferences["break_duration"])

    events = [ScheduleEvent(start_time=e["start_time"], end_time=e["end_time"], activity=e["title"],
                             event_type="calendar", priority="none", reason="Fixed calendar commitment.") for e in fixed_events]
    slots = free_slots(hhmm(work_start), hhmm(work_end), fixed_events)
    ordered = choose_priority(tasks, priority_order)
    scheduled = set()

    for task in ordered:
        duration = int(task["duration"])
        for i, (s, e) in enumerate(slots):
            if e - s < duration:
                continue
            start, finish = s, s + duration
            events.append(ScheduleEvent(start_time=hhmm(start), end_time=hhmm(finish), activity=task["title"],
                                        event_type="work", priority=task["priority"],
                                        reason=f"Prioritized as {task['priority']} with deadline {task['deadline'] or 'none'}."))
            scheduled.add(task["title"])
            replacement = []
            if start - s >= 15:
                replacement.append((s, start))
            after = finish
            if duration >= 60 and break_duration and after + break_duration <= e:
                events.append(ScheduleEvent(start_time=hhmm(after), end_time=hhmm(after + break_duration), activity="Break",
                                            event_type="break", priority="none", reason="Recovery break based on preferences."))
                after += break_duration
            if e - after >= 15:
                replacement.append((after, e))
            slots = slots[:i] + replacement + slots[i+1:]
            break

    # Exercise is added only if it fits and does not collide with fixed/generated events.
    exercise_start = max(minutes("18:00"), work_end) if preferences.get("exercise_preference", "").lower() == "evening" else max(wake, minutes("06:30"))
    exercise_end = exercise_start + 60
    occupied = [(minutes(e.start_time), minutes(e.end_time)) for e in events]
    if exercise_end <= sleep and not any(overlaps(exercise_start, exercise_end, a, b) for a, b in occupied):
        events.append(ScheduleEvent(start_time=hhmm(exercise_start), end_time=hhmm(exercise_end), activity="Exercise",
                                    event_type="exercise", priority="medium", reason="Added according to exercise preference."))

    events.sort(key=lambda e: minutes(e.start_time))
    missing = [t["title"] for t in tasks if t["title"] not in scheduled]
    summary = "Fixed commitments were preserved. The agent chose priorities; Python deterministically calculated and validated the exact slots."
    if missing:
        summary += " Could not fit: " + ", ".join(missing) + "."
    return DailySchedule(date=date, events=events, planning_summary=summary)
