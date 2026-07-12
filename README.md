# Todo Insights Dashboard

A portfolio-style analytics project built around a todo dataset using SQLite, SQL, Python, Pandas, Plotly, and PowerShell.

The `v0.2.0` release expands the project from a simple todo demo into a reproducible analytics workflow with:
- lifecycle-aware task data,
- SQL KPI queries,
- Pandas summary reports,
- Plotly chart generation,
- automated validation between SQL and Python outputs.

## Overview

This project treats todo data as a lightweight analytics case study rather than only a checklist or CRUD example.

The goal is to model task lifecycle behavior and answer reporting questions such as:
- How many tasks are created over time?
- What percentage of tasks are completed?
- How many tasks are overdue?
- How long does task completion usually take?
- Which categories accumulate the most open work?

The repository is designed to show a small but complete analytics pipeline:
1. generate realistic demo data,
2. query and validate KPI metrics,
3. export summary reports,
4. build interactive charts.

## Analytics questions

The current version focuses on five core questions:

1. How many tasks are created by day or week?
2. What is the overall completion rate?
3. How many tasks are overdue?
4. What is the average completion time?
5. Which categories most often remain open?

## Tech stack

- SQLite for the demo database
- SQL for KPI queries
- Python for data generation and analysis
- Pandas for transformations and summary outputs
- Plotly for interactive HTML charts
- PowerShell for automated validation

## Repository structure

```text
todo-insights-dashboard/
├─ data/
│  ├─ todo_demo.db
│  └─ todos.csv
├─ docs/
│  └─ v0.2.0-plan.md
├─ output/
│  ├─ charts/
│  └─ reports/
├─ scripts/
│  ├─ seed_demo_data.py
│  ├─ analyze_todos.py
│  └─ validate_analytics.ps1
├─ sql/
│  └─ kpi_queries.sql
├─ README.md
└─ CHANGELOG.md
```

## Data model

The `todos` table includes lifecycle fields that support analytics:

- `category`
- `status`
- `priority`
- `created_at`
- `due_date`
- `completed_at`

These fields make it possible to calculate trend, completion, and overdue metrics consistently in both SQL and Pandas.

## Prerequisites

Before running the project, make sure you have:

- Python 3.10+
- `pip`
- PowerShell
- Git (optional, but useful for normal repository workflow)

## Setup

Install dependencies before running the analytics workflow:

```powershell
pip install -r requirements.txt
```

## Workflow

### 1. Generate demo data

```powershell
python .\scripts\seed_demo_data.py
```

This script recreates the demo SQLite database and exports a matching CSV dataset.

### 2. Run the analytics pipeline

```powershell
python .\scripts\analyze_todos.py
```

This script:
- loads todo data from SQLite,
- calculates summary metrics,
- builds reporting tables,
- exports report files,
- generates Plotly HTML charts.

### 3. Validate SQL vs Pandas outputs

```powershell
.\scripts\validate_analytics.ps1
```

This validation step compares key metrics from `summary_metrics.csv` against direct SQL queries to make sure the reporting layer is consistent with the source data.

## SQL KPIs

The project includes SQL queries for:
- tasks created by day,
- tasks created by week,
- overall completion rate,
- overdue task count,
- average completion time,
- open tasks by category.

These queries are stored in:

```text
sql/kpi_queries.sql
```

## Outputs

The analytics pipeline generates the following artifacts.

### Reports

- `output/reports/summary_metrics.csv`
- `output/reports/summary_metrics.md`
- `output/reports/created_by_day.csv`
- `output/reports/status_distribution.csv`
- `output/reports/open_tasks_by_category.csv`

### Charts

- `output/charts/tasks_created_over_time.html`
- `output/charts/task_status_distribution.html`
- `output/charts/open_tasks_by_category.html`

## Current metrics

Current seeded demo output:

- Total tasks: 80
- Completed tasks: 42
- Completion rate: 52.5%
- Overdue tasks: 14
- Average completion time: 4.74 days

## Testing

A simple manual smoke test for the current feature:

```powershell
python .\scripts\seed_demo_data.py
python .\scripts\analyze_todos.py
.\scripts\validate_analytics.ps1
start .\output\charts\tasks_created_over_time.html
start .\output\charts\task_status_distribution.html
start .\output\charts\open_tasks_by_category.html
```

Expected validation output:

```text
All analytics checks passed ✅
completion_rate_pct = 52.5
overdue_tasks = 14
avg_completion_days = 4.74
```

## Why this project matters

This project is designed as a portfolio piece that demonstrates:

- SQL querying and KPI design
- reproducible demo data generation
- Pandas-based analysis workflow
- cross-checking metrics between SQL and Python
- interactive chart generation with Plotly
- documentation and analytics storytelling

It is intentionally small enough to understand quickly, but structured enough to show how raw task data can become a reporting workflow.

## Reproducibility

To regenerate the full analytics output from scratch:

```powershell
python .\scripts\seed_demo_data.py
python .\scripts\analyze_todos.py
.\scripts\validate_analytics.ps1
```

If the validation script passes, the generated summary metrics are aligned with the SQL source calculations.

## Known notes

- `data/todo_demo.db` may remain untracked depending on `.gitignore`.
- `data/todos.csv` is committed as a reproducible demo artifact.
- Current charts are exported as standalone HTML files.
- The current version focuses on the analytics workflow rather than a live frontend dashboard UI.

## Next steps

Planned improvements for future versions:

- weekly trend reporting in the summary outputs
- category-level completion rate
- priority-based workload analysis
- dashboard UI improvements
- README screenshots or embedded chart previews
- release-oriented reporting workflow

## Version

Current analytics milestone:

```text
v0.2.0
```

See `CHANGELOG.md` for release history and notable changes.