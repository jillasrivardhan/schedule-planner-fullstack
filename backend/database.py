import json
import sqlite3
from .config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as con:
        con.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT NOT NULL,
                deadline TEXT,
                duration INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        ''')
        con.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                wake_time TEXT NOT NULL,
                sleep_time TEXT NOT NULL,
                preferred_work_start TEXT NOT NULL,
                preferred_work_end TEXT NOT NULL,
                preferred_deep_work_time TEXT NOT NULL,
                break_duration INTEGER NOT NULL,
                exercise_preference TEXT NOT NULL
            )
        ''')
        con.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        ''')
        con.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                schedule_json TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')


def seed_demo():
    with get_connection() as con:
        if con.execute("SELECT COUNT(*) AS c FROM tasks").fetchone()["c"] == 0:
            con.executemany(
                """INSERT INTO tasks (title, description, priority, deadline, duration, status)
                   VALUES (?, ?, ?, ?, ?, 'pending')""",
                [
                    ("Finish RAG project", "Complete remaining project work.", "high", "2026-10-07", 120),
                    ("Learn LangGraph", "Study graphs, state, tools and routing.", "medium", "2026-10-10", 90),
                    ("Exercise", "Workout and movement.", "medium", None, 60),
                    ("Read AI research paper", "Read and take notes.", "low", "2026-10-12", 45),
                ],
            )
        if con.execute("SELECT id FROM preferences WHERE id = 1").fetchone() is None:
            con.execute(
                """INSERT INTO preferences
                (id, wake_time, sleep_time, preferred_work_start, preferred_work_end,
                 preferred_deep_work_time, break_duration, exercise_preference)
                VALUES (1, '06:00', '22:30', '08:00', '20:00', 'morning', 15, 'evening')"""
            )
        if con.execute("SELECT COUNT(*) AS c FROM calendar_events").fetchone()["c"] == 0:
            con.executemany(
                """INSERT INTO calendar_events
                (title, date, start_time, end_time, description)
                VALUES (?, ?, ?, ?, ?)""",
                [
                    ("College", "2026-10-06", "09:00", "12:00", "College"),
                    ("Lunch", "2026-10-06", "13:00", "14:00", "Lunch"),
                    ("Project Meeting", "2026-10-06", "16:00", "17:00", "Project meeting"),
                ],
            )


def get_tasks():
    with get_connection() as con:
        rows = con.execute(
            """SELECT id, title, description, priority, deadline, duration, status
               FROM tasks WHERE status = 'pending'
               ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END,
                        deadline"""
        ).fetchall()
    return [dict(row) for row in rows]


def add_task(data):
    with get_connection() as con:
        cur = con.execute(
            """INSERT INTO tasks (title, description, priority, deadline, duration, status)
               VALUES (?, ?, ?, ?, ?, 'pending')""",
            (data.title, data.description, data.priority.lower(), data.deadline, data.duration),
        )
        return cur.lastrowid


def delete_task(task_id):
    with get_connection() as con:
        con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))


def get_preferences():
    with get_connection() as con:
        row = con.execute(
            """SELECT wake_time, sleep_time, preferred_work_start, preferred_work_end,
                      preferred_deep_work_time, break_duration, exercise_preference
               FROM preferences WHERE id = 1"""
        ).fetchone()
    return dict(row) if row else None


def save_preferences(data):
    with get_connection() as con:
        con.execute(
            """INSERT INTO preferences
               (id, wake_time, sleep_time, preferred_work_start, preferred_work_end,
                preferred_deep_work_time, break_duration, exercise_preference)
               VALUES (1, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 wake_time=excluded.wake_time,
                 sleep_time=excluded.sleep_time,
                 preferred_work_start=excluded.preferred_work_start,
                 preferred_work_end=excluded.preferred_work_end,
                 preferred_deep_work_time=excluded.preferred_deep_work_time,
                 break_duration=excluded.break_duration,
                 exercise_preference=excluded.exercise_preference""",
            (data.wake_time, data.sleep_time, data.preferred_work_start, data.preferred_work_end,
             data.preferred_deep_work_time, data.break_duration, data.exercise_preference),
        )


def get_local_calendar(target_date):
    with get_connection() as con:
        rows = con.execute(
            """SELECT id, title, date, start_time, end_time, description
               FROM calendar_events WHERE date = ? ORDER BY start_time""",
            (target_date,),
        ).fetchall()
    return [{**dict(row), "source": "local"} for row in rows]


def save_schedule(target_date, schedule, status="approved"):
    with get_connection() as con:
        con.execute(
            "INSERT INTO schedules (date, schedule_json, status) VALUES (?, ?, ?)",
            (target_date, json.dumps(schedule), status),
        )


def get_latest_schedule(target_date):
    with get_connection() as con:
        row = con.execute(
            """SELECT id, date, schedule_json, status FROM schedules
               WHERE date = ? ORDER BY id DESC LIMIT 1""",
            (target_date,),
        ).fetchone()
    if not row:
        return None
    result = dict(row)
    result["schedule_json"] = json.loads(result["schedule_json"])
    return result
