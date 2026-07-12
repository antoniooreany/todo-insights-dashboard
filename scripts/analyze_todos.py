from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "todo_demo.db"
OUTPUT_DIR = ROOT / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
REPORTS_DIR = OUTPUT_DIR / "reports"


def ensure_output_dirs() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_todos() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM todos", conn)

    for col in ["created_at", "due_date", "completed_at"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def build_summary_metrics(df: pd.DataFrame) -> pd.DataFrame:
    total_tasks = len(df)
    completed_tasks = int((df["status"] == "completed").sum())
    open_tasks = int((df["status"] == "open").sum())
    in_progress_tasks = int((df["status"] == "in_progress").sum())

    overdue_tasks = int(
        ((df["due_date"].notna()) &
         (df["due_date"] < pd.Timestamp.now()) &
         (df["status"] != "completed")).sum()
    )

    completion_rate = round((completed_tasks / total_tasks) * 100, 2) if total_tasks else 0.0

    completed_df = df[df["status"] == "completed"].copy()
    completed_df["completion_days"] = (
        completed_df["completed_at"] - completed_df["created_at"]
    ).dt.total_seconds() / 86400
    avg_completion_days = round(completed_df["completion_days"].mean(), 2)

    summary = pd.DataFrame(
        [
            {"metric": "total_tasks", "value": total_tasks},
            {"metric": "completed_tasks", "value": completed_tasks},
            {"metric": "open_tasks", "value": open_tasks},
            {"metric": "in_progress_tasks", "value": in_progress_tasks},
            {"metric": "overdue_tasks", "value": overdue_tasks},
            {"metric": "completion_rate_pct", "value": completion_rate},
            {"metric": "avg_completion_days", "value": avg_completion_days},
        ]
    )
    return summary


def build_created_by_day(df: pd.DataFrame) -> pd.DataFrame:
    created = (
        df.assign(created_day=df["created_at"].dt.date)
        .groupby("created_day", as_index=False)
        .size()
        .rename(columns={"size": "tasks_created"})
    )
    return created


def build_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    status_dist = (
        df.groupby("status", as_index=False)
        .size()
        .rename(columns={"size": "task_count"})
    )
    return status_dist


def build_open_tasks_by_category(df: pd.DataFrame) -> pd.DataFrame:
    open_cat = (
        df[df["status"] != "completed"]
        .groupby("category", as_index=False)
        .size()
        .rename(columns={"size": "open_tasks"})
        .sort_values(["open_tasks", "category"], ascending=[False, True])
    )
    return open_cat


def save_summary_markdown(summary: pd.DataFrame) -> None:
    lines = [
        "# Summary Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]

    for _, row in summary.iterrows():
        lines.append(f"| {row['metric']} | {row['value']} |")

    output_path = REPORTS_DIR / "summary_metrics.md"
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_chart_created_by_day(created_by_day: pd.DataFrame) -> None:
    fig = px.line(
        created_by_day,
        x="created_day",
        y="tasks_created",
        markers=True,
        title="Tasks Created Over Time",
    )
    fig.update_layout(template="plotly_white")
    fig.write_html(CHARTS_DIR / "tasks_created_over_time.html")


def save_chart_status_distribution(status_dist: pd.DataFrame) -> None:
    fig = px.bar(
        status_dist,
        x="status",
        y="task_count",
        color="status",
        title="Task Status Distribution",
    )
    fig.update_layout(template="plotly_white", showlegend=False)
    fig.write_html(CHARTS_DIR / "task_status_distribution.html")


def save_chart_open_by_category(open_by_category: pd.DataFrame) -> None:
    fig = px.bar(
        open_by_category,
        x="open_tasks",
        y="category",
        orientation="h",
        title="Open Tasks by Category",
    )
    fig.update_layout(template="plotly_white", yaxis={"categoryorder": "total ascending"})
    fig.write_html(CHARTS_DIR / "open_tasks_by_category.html")


def main() -> None:
    ensure_output_dirs()

    df = load_todos()
    summary = build_summary_metrics(df)
    created_by_day = build_created_by_day(df)
    status_dist = build_status_distribution(df)
    open_by_category = build_open_tasks_by_category(df)

    summary.to_csv(REPORTS_DIR / "summary_metrics.csv", index=False)
    created_by_day.to_csv(REPORTS_DIR / "created_by_day.csv", index=False)
    status_dist.to_csv(REPORTS_DIR / "status_distribution.csv", index=False)
    open_by_category.to_csv(REPORTS_DIR / "open_tasks_by_category.csv", index=False)

    save_summary_markdown(summary)
    save_chart_created_by_day(created_by_day)
    save_chart_status_distribution(status_dist)
    save_chart_open_by_category(open_by_category)

    print("Generated files:")
    print(f"- {REPORTS_DIR / 'summary_metrics.csv'}")
    print(f"- {REPORTS_DIR / 'summary_metrics.md'}")
    print(f"- {REPORTS_DIR / 'created_by_day.csv'}")
    print(f"- {REPORTS_DIR / 'status_distribution.csv'}")
    print(f"- {REPORTS_DIR / 'open_tasks_by_category.csv'}")
    print(f"- {CHARTS_DIR / 'tasks_created_over_time.html'}")
    print(f"- {CHARTS_DIR / 'task_status_distribution.html'}")
    print(f"- {CHARTS_DIR / 'open_tasks_by_category.html'}")


if __name__ == "__main__":
    main()