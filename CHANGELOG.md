# Changelog

All notable changes to this project will be documented in this file.

The project follows a simple semantic versioning style, and changelog entries are grouped in a human-readable format.

## [Unreleased]

### Added

- Placeholder for upcoming changes.

## [0.2.0] - 2026-07-12

### Added

- Added `docs/v0.2.0-plan.md` to define the analytics roadmap.
- Added lifecycle analytics fields to the todo model: `category`, `created_at`, `due_date`, `completed_at`, and `priority`.
- Added `scripts/seed_demo_data.py` to generate realistic demo tasks and export CSV data.
- Added `sql/kpi_queries.sql` for KPI calculations and reporting queries.
- Added `scripts/analyze_todos.py` to generate analytics summaries and export report files.
- Added Plotly chart generation for:
  - `tasks_created_over_time.html`
  - `task_status_distribution.html`
  - `open_tasks_by_category.html`
- Added `scripts/validate_analytics.ps1` to compare SQL results against generated summary metrics.
- Added generated report outputs in `output/reports/`.
- Added generated chart outputs in `output/charts/`.

### Changed

- Expanded the project from a simple todo demo into a portfolio-style analytics workflow.
- Improved reproducibility through seeded demo data, automated summaries, generated chart outputs, and validation checks.
- Updated `README.md` with a clearer project overview, setup instructions, workflow, outputs, testing steps, and reproducibility notes.
- Updated repository structure to support analytics reporting and validation workflows.

## [0.1.0] - 2026-07-12

### Added

- Initial project release.
- Base todo insights project structure.
- First tagged GitHub release for `v0.1.0`.