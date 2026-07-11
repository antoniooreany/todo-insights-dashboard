from pathlib import Path
import sqlite3
import pandas as pd
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CHARTS_DIR = BASE_DIR / "charts"
DB_PATH = DATA_DIR / "todos.db"


def read_query(conn, query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, conn)


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError("Database not found. Run scripts/seed_data.py first.")

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    total_tasks = read_query(conn, "SELECT COUNT(*) AS total_tasks FROM todos")
    status_breakdown = read_query(conn, "SELECT is_done, COUNT(*) AS task_count FROM todos GROUP BY is_done")
    completion_rate = read_query(conn, "SELECT ROUND(100.0 * SUM(CASE WHEN is_done = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS completion_rate FROM todos")
    overdue_tasks = read_query(conn, "SELECT COUNT(*) AS overdue_tasks FROM todos WHERE is_done = 0 AND due_date IS NOT NULL AND date(due_date) < date('now')")
    avg_completion = read_query(conn, "SELECT ROUND(AVG(julianday(completed_at) - julianday(created_at)), 2) AS avg_completion_days FROM todos WHERE completed_at IS NOT NULL")

    created_df = read_query(conn, "SELECT date(created_at) AS day, COUNT(*) AS created_count FROM todos GROUP BY date(created_at) ORDER BY day")
    completed_df = read_query(conn, "SELECT date(completed_at) AS day, COUNT(*) AS completed_count FROM todos WHERE completed_at IS NOT NULL GROUP BY date(completed_at) ORDER BY day")
    category_df = read_query(conn, "SELECT category, COUNT(*) AS task_count FROM todos GROUP BY category ORDER BY task_count DESC")

    conn.close()

    fig_created = px.line(created_df, x="day", y="created_count", markers=True, title="Tasks created over time")
    fig_created.update_layout(xaxis_title="Date", yaxis_title="Tasks created")
    fig_created.write_html(CHARTS_DIR / "created_over_time.html")

    fig_completed = px.bar(completed_df, x="day", y="completed_count", title="Tasks completed over time")
    fig_completed.update_layout(xaxis_title="Date", yaxis_title="Tasks completed")
    fig_completed.write_html(CHARTS_DIR / "completed_over_time.html")

    fig_category = px.bar(category_df, x="category", y="task_count", title="Tasks by category")
    fig_category.update_layout(xaxis_title="Category", yaxis_title="Task count")
    fig_category.write_html(CHARTS_DIR / "tasks_by_category.html")

    summary_path = BASE_DIR / "analysis_summary.md"
    summary_path.write_text(
        "\n".join([
            "# Analysis Summary",
            "",
            f"- Total tasks: {int(total_tasks.iloc[0, 0])}",
            f"- Completion rate: {float(completion_rate.iloc[0, 0]):.2f}%",
            f"- Overdue tasks: {int(overdue_tasks.iloc[0, 0])}",
            f"- Average completion time: {float(avg_completion.iloc[0, 0]):.2f} days",
            "",
            "## Status breakdown",
            status_breakdown.to_markdown(index=False),
            "",
            "## Category breakdown",
            category_df.to_markdown(index=False),
        ]),
        encoding="utf-8",
    )

    print("Analysis complete.")
    print(f"Charts saved to {CHARTS_DIR}")
    print(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    main()
