from pathlib import Path
import random
import sqlite3
from datetime import datetime, timedelta
import csv

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "todos.db"
CSV_PATH = DATA_DIR / "sample_todos.csv"

random.seed(42)

CATEGORIES = ["work", "study", "personal", "health", "admin"]
PRIORITIES = ["low", "medium", "high"]
TITLE_PREFIXES = {
    "work": ["Prepare", "Review", "Update", "Plan", "Document"],
    "study": ["Read", "Practice", "Finish", "Revise", "Summarize"],
    "personal": ["Call", "Organize", "Buy", "Schedule", "Clean"],
    "health": ["Walk", "Book", "Track", "Prepare", "Stretch"],
    "admin": ["Submit", "Check", "Renew", "Archive", "Verify"],
}
TITLE_OBJECTS = {
    "work": ["project notes", "sprint tasks", "client feedback", "API docs", "weekly plan"],
    "study": ["SQL exercises", "Python lesson", "statistics notes", "pandas tutorial", "flashcards"],
    "personal": ["groceries", "weekend plan", "home checklist", "messages", "budget notes"],
    "health": ["meal prep", "sleep log", "training routine", "doctor appointment", "water intake"],
    "admin": ["invoice", "account settings", "documents", "calendar", "registration"],
}


def random_title(category: str) -> str:
    return f"{random.choice(TITLE_PREFIXES[category])} {random.choice(TITLE_OBJECTS[category])}"


def build_rows(n: int = 120):
    now = datetime.now()
    rows = []
    for i in range(1, n + 1):
        category = random.choices(CATEGORIES, weights=[35, 25, 15, 15, 10], k=1)[0]
        priority = random.choices(PRIORITIES, weights=[20, 55, 25], k=1)[0]
        created_at = now - timedelta(days=random.randint(0, 59), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        due_date = created_at + timedelta(days=random.randint(1, 12))
        done = random.random() < 0.65
        completed_at = None
        if done:
            completed_at = created_at + timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))
            if completed_at > now:
                completed_at = now - timedelta(hours=random.randint(1, 12))
        row = {
            "id": i,
            "title": random_title(category),
            "description": f"Auto-generated sample task #{i} for analytics practice.",
            "category": category,
            "priority": priority,
            "is_done": int(done),
            "created_at": created_at.replace(microsecond=0).isoformat(sep=" "),
            "completed_at": completed_at.replace(microsecond=0).isoformat(sep=" ") if completed_at else "",
            "due_date": due_date.date().isoformat(),
        }
        rows.append(row)
    return rows


def init_db(conn: sqlite3.Connection):
    conn.execute("DROP TABLE IF EXISTS todos")
    conn.execute(
        """
        CREATE TABLE todos (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL DEFAULT 'general',
            priority TEXT NOT NULL DEFAULT 'medium',
            is_done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            due_date TEXT
        )
        """
    )
    conn.commit()


def save_db(rows):
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    conn.executemany(
        """
        INSERT INTO todos (id, title, description, category, priority, is_done, created_at, completed_at, due_date)
        VALUES (:id, :title, :description, :category, :priority, :is_done, :created_at, :completed_at, :due_date)
        """,
        rows,
    )
    conn.commit()
    conn.close()


def save_csv(rows):
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "title", "description", "category", "priority", "is_done", "created_at", "completed_at", "due_date"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    save_db(rows)
    save_csv(rows)
    print(f"Created {DB_PATH}")
    print(f"Created {CSV_PATH}")
    print(f"Seeded {len(rows)} todo rows")


if __name__ == "__main__":
    main()
