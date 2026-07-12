from __future__ import annotations

import csv
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "todo_demo.db"
CSV_PATH = DATA_DIR / "todos.csv"

TASK_COUNT = 80
RANDOM_SEED = 42

CATEGORIES = ["Work", "Personal", "Study", "Health", "Admin", "Finance"]
PRIORITIES = ["low", "medium", "high"]
STATUSES = ["open", "in_progress", "completed"]

TITLE_TEMPLATES = {
    "Work": [
        "Prepare sprint summary",
        "Review pull request",
        "Refactor analytics module",
        "Update project roadmap",
        "Write release notes",
        "Investigate failing test",
        "Plan dashboard improvements",
    ],
    "Personal": [
        "Buy groceries",
        "Organize desk",
        "Call family",
        "Plan weekly budget",
        "Book appointment",
        "Clean apartment",
        "Read 20 pages",
    ],
    "Study": [
        "Practice SQL queries",
        "Finish pandas exercise",
        "Review Python typing",
        "Read analytics article",
        "Complete plotting tutorial",
        "Revise database basics",
        "Take notes on testing",
    ],
    "Health": [
        "Morning walk",
        "Stretch for 20 minutes",
        "Prepare healthy meal",
        "Track water intake",
        "Schedule workout",
        "Sleep before midnight",
        "Meditation session",
    ],
    "Admin": [
        "Reply to emails",
        "Archive old files",
        "Update documentation",
        "Rename project assets",
        "Sort downloads folder",
        "Check invoices",
        "Backup important files",
    ],
    "Finance": [
        "Review monthly expenses",
        "Pay utility bill",
        "Update savings tracker",
        "Check subscription costs",
        "Categorize transactions",
        "Export bank statement",
        "Plan next month budget",
    ],
}

DESCRIPTION_SUFFIXES = [
    "and document the result.",
    "before the next weekly review.",
    "with enough detail for reuse.",
    "and keep the workflow reproducible.",
    "while tracking the main blockers.",
    "and verify the expected output.",
]


def iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def choose_status() -> str:
    roll = random.random()
    if roll < 0.58:
        return "completed"
    if roll < 0.80:
        return "open"
    return "in_progress"


def choose_priority() -> str:
    roll = random.random()
    if roll < 0.25:
        return "high"
    if roll < 0.70:
        return "medium"
    return "low"


def build_task(task_id: int, now: datetime) -> tuple:
    category = random.choice(CATEGORIES)
    title = random.choice(TITLE_TEMPLATES[category])
    description = f"{title} {random.choice(DESCRIPTION_SUFFIXES)}"
    status = choose_status()
    priority = choose_priority()

    created_at = now - timedelta(
        days=random.randint(0, 59),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    due_date = created_at + timedelta(days=random.randint(1, 14))

    completed_at = None
    if status == "completed":
        completion_days = random.randint(0, 10)
        completion_hours = random.randint(0, 23)
        completed_at = created_at + timedelta(days=completion_days, hours=completion_hours)
        if completed_at > now:
            completed_at = now - timedelta(hours=random.randint(1, 12))

    if status in {"open", "in_progress"}:
        if random.random() < 0.35:
            due_date = now - timedelta(days=random.randint(1, 10))
        else:
            due_date = now + timedelta(days=random.randint(1, 12))

    return (
        task_id,
        title,
        description,
        category,
        status,
        priority,
        iso(created_at),
        iso(due_date),
        iso(completed_at),
    )


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def recreate_database(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS todos")
    cursor.execute(
        """
        CREATE TABLE todos (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'completed')),
            priority TEXT CHECK (priority IN ('low', 'medium', 'high')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            due_date TEXT,
            completed_at TEXT
        )
        """
    )
    connection.commit()


def insert_tasks(connection: sqlite3.Connection, tasks: list[tuple]) -> None:
    cursor = connection.cursor()
    cursor.executemany(
        """
        INSERT INTO todos (
            id,
            title,
            description,
            category,
            status,
            priority,
            created_at,
            due_date,
            completed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        tasks,
    )
    connection.commit()


def export_csv(tasks: list[tuple]) -> None:
    headers = [
        "id",
        "title",
        "description",
        "category",
        "status",
        "priority",
        "created_at",
        "due_date",
        "completed_at",
    ]

    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(tasks)


def print_summary(tasks: list[tuple], now: datetime) -> None:
    total = len(tasks)
    completed = sum(1 for t in tasks if t[4] == "completed")
    open_tasks = sum(1 for t in tasks if t[4] == "open")
    in_progress = sum(1 for t in tasks if t[4] == "in_progress")
    overdue = sum(
        1
        for t in tasks
        if t[7] is not None
        and datetime.strptime(t[7], "%Y-%m-%d %H:%M:%S") < now
        and t[4] != "completed"
    )

    print(f"Created {total} tasks")
    print(f"Completed: {completed}")
    print(f"Open: {open_tasks}")
    print(f"In progress: {in_progress}")
    print(f"Overdue: {overdue}")
    print(f"SQLite DB: {DB_PATH}")
    print(f"CSV export: {CSV_PATH}")


def main() -> None:
    random.seed(RANDOM_SEED)
    ensure_data_dir()

    now = datetime.now()
    tasks = [build_task(task_id=i, now=now) for i in range(1, TASK_COUNT + 1)]

    with sqlite3.connect(DB_PATH) as connection:
        recreate_database(connection)
        insert_tasks(connection, tasks)

    export_csv(tasks)
    print_summary(tasks, now)


if __name__ == "__main__":
    main()