# Todo Insights Dashboard

Todo Insights Dashboard is a portfolio project that explores task-management data with Python, SQLite, Pandas, and Plotly. It builds an analytics layer around a simple todo domain and focuses on practical reporting questions such as completion rate, overdue workload, task volume over time, and category distribution.

## Project overview

This project was designed as a small data-analysis case study based on a familiar backend-style domain: todos. Instead of building another CRUD-only service, it extends the same business area with reporting, aggregation, and visualization.

The project answers questions such as:
- How many tasks were created over time?
- How many tasks were completed over time?
- What percentage of tasks were completed?
- How many open tasks are overdue?
- Which categories contain the highest task volume?
- How long does it take to complete tasks on average?

## Tech stack

- Python 3
- SQLite
- Pandas
- Plotly
- Tabulate

## Repository structure

```text
todo-insights-dashboard/
├── data/
│   ├── sample_todos.csv
│   └── todos.db
├── charts/
│   ├── completed_over_time.html
│   ├── created_over_time.html
│   └── tasks_by_category.html
├── scripts/
│   ├── analyze_todos.py
│   └── seed_data.py
├── sql/
│   └── queries.sql
├── analysis_summary.md
├── requirements.txt
└── README.md
```

## Dataset

The dataset is generated locally for demonstration purposes. The seed script creates realistic sample todo records with the following fields:

- `id`
- `title`
- `description`
- `category`
- `priority`
- `is_done`
- `created_at`
- `completed_at`
- `due_date`

The generated records simulate a small productivity dataset across categories such as work, study, personal, health, and admin.

## Analytical scope

The project focuses on a compact but useful reporting layer.

### Core metrics

- Total number of tasks
- Completion rate
- Open vs completed tasks
- Number of overdue tasks
- Average completion time in days

### Visualizations

- Tasks created over time
- Tasks completed over time
- Tasks by category

## How to run

### 1. Create and activate a virtual environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate sample data

```bash
python scripts/seed_data.py
```

This step creates:
- `data/todos.db`
- `data/sample_todos.csv`

### 4. Run the analysis

```bash
python scripts/analyze_todos.py
```

This step creates:
- `analysis_summary.md`
- `charts/created_over_time.html`
- `charts/completed_over_time.html`
- `charts/tasks_by_category.html`

## SQL examples

The repository includes reusable SQL queries in `sql/queries.sql`, including:

- total task count
- open vs done breakdown
- completion rate
- overdue tasks
- average completion time
- tasks created over time
- tasks completed over time
- tasks by category

## Example questions answered

The analysis layer is intended to simulate the kind of reporting logic often needed in real applications:

- Are tasks being completed at a healthy rate?
- Is overdue work increasing?
- Which categories generate the most workload?
- Is output steady over time or inconsistent?
- How long does task completion usually take?

## Why this project matters

This repository demonstrates more than basic scripting. It shows the ability to:

- work with structured data
- generate and store records in SQLite
- write analytical SQL queries
- transform data with Pandas
- build visual outputs with Plotly
- organize a small but complete analytics project for GitHub

It also complements a backend portfolio well, because it shows reporting and data-analysis skills on top of a domain that could also exist as an API-based service.

## Possible next steps

Future improvements could include:

- connecting the analysis directly to a FastAPI todo backend
- adding a Streamlit or Dash dashboard UI
- introducing real exported app data instead of generated demo data
- adding more advanced time-based metrics, such as weekly completion rate or overdue trends
- extending the model with users, labels, or projects

## Author note

This project is intended as a junior-friendly portfolio piece that connects backend thinking with data analysis. It can stand alone as a small analytics repository or later evolve into a broader todo ecosystem project.
