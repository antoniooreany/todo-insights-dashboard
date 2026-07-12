# Todo Insights Dashboard

Todo Insights Dashboard is a portfolio project that explores task-management data with Python, SQLite, Pandas, and Plotly. It builds an analytics layer around a simple todo domain and focuses on practical reporting questions such as completion rate, overdue workload, task volume over time, category distribution, and repository-level documentation.

## Project overview

This project was designed as a small data-analysis case study based on a familiar backend-style domain: todos. Instead of building another CRUD-only service, it extends the same business area with reporting, aggregation, visualization, and repository introspection.

The project answers questions such as:
- How many tasks were created over time?
- How many tasks were completed over time?
- What percentage of tasks were completed?
- How many open tasks are overdue?
- Which categories contain the highest task volume?
- How long does it take to complete tasks on average?
- How is the repository structured and documented for reviewers?

## Highlights

- Demonstrates Python data analysis on top of a simple todo domain.
- Uses SQLite as a lightweight local analytical store.
- Transforms and summarizes data with Pandas.
- Produces interactive visualizations with Plotly.
- Includes reusable SQL queries for core reporting logic.
- Generates a development-oriented project report for repository review and reproducibility.

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
│   ├── generate_project_report.py
│   └── seed_data.py
├── sql/
│   └── queries.sql
├── .project-report/
│   ├── PROJECT_REPORT_YYYY-MM-DD_HH-MM-SS.md
│   └── project-report_YYYY-MM-DD_HH-MM-SS.json
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

## Requirements

- Python 3.10+ recommended
- `pip`
- Git, if you want repository metadata in the generated project report

## How to run

### 1. Clone the repository

```bash
git clone https://github.com/antoniooreany/todo-insights-dashboard.git
cd todo-insights-dashboard
```

### 2. Create and activate a virtual environment

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

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate sample data

```bash
python scripts/seed_data.py
```

This step creates:
- `data/todos.db`
- `data/sample_todos.csv`

### 5. Run the analysis

```bash
python scripts/analyze_todos.py
```

This step creates:
- `analysis_summary.md`
- `charts/created_over_time.html`
- `charts/completed_over_time.html`
- `charts/tasks_by_category.html`

### 6. Generate a project report

```bash
python scripts/generate_project_report.py
```

This step creates timestamped report files such as:
- `.project-report/PROJECT_REPORT_2026-07-12_13-32-07.md`
- `.project-report/project-report_2026-07-12_13-32-07.json`

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

## Project report generator

The repository includes a helper script that generates a detailed development-oriented project report. The purpose of this script is to provide a fast but comprehensive understanding of the repository for a developer, reviewer, maintainer, or collaborator.

Instead of showing only a file tree, the generated report gives a broader technical picture of the project. It is designed to help a reader understand the structure, architecture, dependencies, generated outputs, and current repository state without manually opening every file.

The generated report is intended to answer questions such as:
- What files and directories make up the project?
- What is the project trying to do at a high level?
- How is the repository organized internally?
- Which source files are most important?
- What dependencies does the project declare?
- Which Python modules are imported across the codebase?
- What functions and classes exist in the Python scripts?
- What SQL assets are present in the repository?
- Which generated outputs and data files already exist?
- What is the current Git state of the repository?
- How can another developer reproduce the same project state locally?

### Report contents

The generated project report includes:
- a report purpose section that explains why the document exists
- a project overview section with a high-level summary of the repository
- an architecture summary that describes the main layers of the project
- a project summary with file counts and total repository size
- Git repository metadata, including current branch, latest commit, recent commits, remotes, tracked file count, and working tree status
- a complete repository tree, excluding non-essential directories
- file type counts and size statistics
- a list of the largest files in the repository
- a dependency list parsed from `requirements.txt`
- a combined list of imported Python modules
- a README preview
- a reproducibility section that explains how to recreate the repository state on a fresh machine
- per-file Python source analysis, including imported modules, functions, classes, and `main` entry-point detection
- SQL file analysis with a basic statement summary
- previews of important files such as `README.md`, `analysis_summary.md`, Python scripts, SQL files, configuration files, and selected data-related files
- a machine-readable JSON export for downstream automation or tooling

### Reproducibility section

The generated report includes a dedicated `How to reproduce this state` section. This part explains how to:

1. clone the repository
2. create and activate a virtual environment
3. install dependencies
4. generate sample data
5. run the analytics script
6. generate the project report itself

This makes the report more self-contained and more useful for onboarding, review, handoff, or portfolio presentation.

### Report naming convention

The report filenames include a timestamp in the format `YYYY-MM-DD_HH-MM-SS`. This makes it possible to keep multiple historical snapshots of the project without overwriting previous reports. It also makes generated files easier to sort chronologically and compare over time.

### Excluded directories

The script automatically excludes common non-essential directories such as:
- `.venv`
- `venv`
- `.git`
- `__pycache__`
- `node_modules`
- `build`
- `dist`
- `.project-report`

This helps the report focus on actual source code, documentation, data, and generated outputs rather than virtual environments, cache folders, or previously generated reports.

## Example questions answered

The analysis layer is intended to simulate the kind of reporting logic often needed in real applications:

- Are tasks being completed at a healthy rate?
- Is overdue work increasing?
- Which categories generate the most workload?
- Is output steady over time or inconsistent?
- How long does task completion usually take?

The repository report layer adds another dimension of practical review:

- What does the repository contain right now?
- Which files are central to the project?
- What does the Git working tree look like?
- Is the project easy to inspect, reproduce, and hand off to another developer?

## Outputs

After running all scripts, the repository can contain these generated outputs:

- `data/todos.db`
- `data/sample_todos.csv`
- `analysis_summary.md`
- `charts/created_over_time.html`
- `charts/completed_over_time.html`
- `charts/tasks_by_category.html`
- `.project-report/PROJECT_REPORT_YYYY-MM-DD_HH-MM-SS.md`
- `.project-report/project-report_YYYY-MM-DD_HH-MM-SS.json`

## Why this project matters

This repository demonstrates more than basic scripting. It shows the ability to:

- work with structured data
- generate and store records in SQLite
- write analytical SQL queries
- transform data with Pandas
- build visual outputs with Plotly
- organize a small but complete analytics project for GitHub
- generate repository-level technical documentation automatically
- expose project structure and Git state for review and maintenance workflows
- support reproducibility through clear setup and regeneration steps

It also complements a backend portfolio well, because it shows reporting and data-analysis skills on top of a domain that could also exist as an API-based service. The additional reporting utility makes the project feel more complete from an engineering and documentation perspective.

## Possible next steps

Future improvements could include:

- connecting the analysis directly to a FastAPI todo backend
- adding a Streamlit or Dash dashboard UI
- introducing real exported app data instead of generated demo data
- adding more advanced time-based metrics, such as weekly completion rate or overdue trends
- extending the model with users, labels, or projects
- exporting charts as images in addition to HTML
- extending the project report with test discovery, environment diagnostics, and repository health checks

## License

This project can be released under the MIT License.

## Author note

This project is intended as a junior-friendly portfolio piece that connects backend thinking with data analysis. It can stand alone as a small analytics repository or later evolve into a broader todo ecosystem project.

It also demonstrates an additional layer that is useful in real engineering workflows: the ability to inspect, summarize, and document a repository automatically for onboarding, review, and maintenance.


## Testing

Run tests locally with:

```bash
pytest
```

## Continuous integration

This repository uses GitHub Actions to run automated tests on:
- pushes to feature, develop, and main branches
- pull requests targeting develop and main
