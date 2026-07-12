from __future__ import annotations

import ast
import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


EXCLUDED_DIRECTORIES = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".project-report",
}

IMPORTANT_FILE_NAMES = {
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "Dockerfile",
    "Makefile",
    "analysis_summary.md",
    ".gitignore",
}

IMPORTANT_EXTENSIONS = {
    ".py",
    ".sql",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".csv",
    ".txt",
}

TEXT_PREVIEW_MAX_LINES = 30
TEXT_PREVIEW_MAX_CHARACTERS = 3000
LARGEST_FILES_LIMIT = 15
IMPORTANT_FILE_PREVIEW_LIMIT = 50
COMMAND_TIMEOUT_SECONDS = 10


def is_excluded_directory(name: str) -> bool:
    return name in EXCLUDED_DIRECTORIES


def relative_path(path: Path, base: Path) -> str:
    return str(path.relative_to(base)).replace("\\", "/")


def read_text_preview(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as file:
            lines = []
            for _, line in zip(range(TEXT_PREVIEW_MAX_LINES), file):
                lines.append(line.rstrip("\n"))
        text = "\n".join(lines)
        if len(text) > TEXT_PREVIEW_MAX_CHARACTERS:
            text = text[:TEXT_PREVIEW_MAX_CHARACTERS] + "\n... [truncated]"
        return text
    except Exception:
        return "[preview unavailable]"


def build_project_tree(root: Path) -> list[str]:
    def walk_directory(current: Path, prefix: str = "") -> list[str]:
        entries = [
            path
            for path in sorted(current.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
            if not (path.is_dir() and is_excluded_directory(path.name))
        ]
        lines: list[str] = []
        for index, entry in enumerate(entries):
            is_last = index == len(entries) - 1
            branch = "└── " if is_last else "├── "
            lines.append(prefix + branch + entry.name)
            if entry.is_dir():
                child_prefix = prefix + ("    " if is_last else "│   ")
                lines.extend(walk_directory(entry, child_prefix))
        return lines

    return [root.name] + walk_directory(root)


def parse_python_imports(path: Path) -> dict:
    result = {
        "imports": [],
        "import_from_modules": [],
        "functions": [],
        "classes": [],
        "has_main_guard": False,
    }

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except Exception:
        return result

    imports = set()
    import_from_modules = set()
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module if node.module else "."
            import_from_modules.add(module_name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    if 'if __name__ == "__main__":' in source or "if __name__ == '__main__':" in source:
        result["has_main_guard"] = True

    result["imports"] = sorted(imports)
    result["import_from_modules"] = sorted(import_from_modules)
    result["functions"] = sorted(set(functions))
    result["classes"] = sorted(set(classes))
    return result


def parse_requirements(path: Path) -> list[str]:
    if not path.exists():
        return []

    dependencies = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            dependencies.append(stripped)
    except Exception:
        return []

    return dependencies


def summarize_sql_file(path: Path) -> dict:
    summary = {
        "select_count": 0,
        "insert_count": 0,
        "update_count": 0,
        "delete_count": 0,
        "create_count": 0,
    }

    try:
        content = path.read_text(encoding="utf-8", errors="replace").lower()
    except Exception:
        return summary

    summary["select_count"] = content.count("select ")
    summary["insert_count"] = content.count("insert ")
    summary["update_count"] = content.count("update ")
    summary["delete_count"] = content.count("delete ")
    summary["create_count"] = content.count("create ")

    return summary


def classify_file(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix == ".py":
        return "Python source file"
    if suffix == ".sql":
        return "SQL file"
    if suffix == ".md":
        return "Markdown documentation"
    if suffix in {".json", ".toml", ".yaml", ".yml"}:
        return "Configuration or structured data file"
    if suffix == ".csv":
        return "Comma-separated data file"
    if suffix in {".db", ".sqlite3"}:
        return "SQLite database file"
    if suffix == ".html":
        return "HTML output file"
    if suffix == ".txt":
        return "Text file"
    return "Other file"


def run_command(command: list[str], working_directory: Path) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            check=False,
        )
        return {
            "command": " ".join(command),
            "return_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "success": result.returncode == 0,
        }
    except FileNotFoundError:
        return {
            "command": " ".join(command),
            "return_code": None,
            "stdout": "",
            "stderr": f"Command not found: {command[0]}",
            "success": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(command),
            "return_code": None,
            "stdout": "",
            "stderr": f"Command timed out after {COMMAND_TIMEOUT_SECONDS} seconds",
            "success": False,
        }


def collect_git_information(project_path: Path) -> dict:
    git_version = run_command(["git", "--version"], project_path)
    inside_work_tree = run_command(["git", "rev-parse", "--is-inside-work-tree"], project_path)

    git_info = {
        "git_available": git_version["success"],
        "inside_git_repository": inside_work_tree["success"] and inside_work_tree["stdout"].lower() == "true",
        "git_version": git_version.get("stdout", ""),
        "repository_root": "",
        "current_branch": "",
        "current_commit_hash": "",
        "current_commit_short_hash": "",
        "current_commit_message": "",
        "working_tree_status_short": "",
        "working_tree_status_porcelain": "",
        "tracked_file_count": None,
        "recent_commits": [],
        "remotes": "",
        "errors": [],
    }

    if not git_info["git_available"]:
        git_info["errors"].append(git_version["stderr"] or "Git is not available")
        return git_info

    if not git_info["inside_git_repository"]:
        if inside_work_tree["stderr"]:
            git_info["errors"].append(inside_work_tree["stderr"])
        return git_info

    repository_root = run_command(["git", "rev-parse", "--show-toplevel"], project_path)
    current_branch = run_command(["git", "branch", "--show-current"], project_path)
    current_commit_hash = run_command(["git", "rev-parse", "HEAD"], project_path)
    current_commit_short_hash = run_command(["git", "rev-parse", "--short", "HEAD"], project_path)
    current_commit_message = run_command(["git", "log", "-1", "--pretty=%s"], project_path)
    status_short = run_command(["git", "status", "--short"], project_path)
    status_porcelain = run_command(["git", "status", "--porcelain=v1"], project_path)
    tracked_file_count = run_command(["git", "ls-files"], project_path)
    recent_commits = run_command(["git", "log", "--oneline", "-5"], project_path)
    remotes = run_command(["git", "remote", "-v"], project_path)

    git_info["repository_root"] = repository_root.get("stdout", "")
    git_info["current_branch"] = current_branch.get("stdout", "")
    git_info["current_commit_hash"] = current_commit_hash.get("stdout", "")
    git_info["current_commit_short_hash"] = current_commit_short_hash.get("stdout", "")
    git_info["current_commit_message"] = current_commit_message.get("stdout", "")
    git_info["working_tree_status_short"] = status_short.get("stdout", "")
    git_info["working_tree_status_porcelain"] = status_porcelain.get("stdout", "")
    git_info["tracked_file_count"] = len(tracked_file_count.get("stdout", "").splitlines()) if tracked_file_count.get("stdout") else 0
    git_info["recent_commits"] = recent_commits.get("stdout", "").splitlines() if recent_commits.get("stdout") else []
    git_info["remotes"] = remotes.get("stdout", "")

    for command_result in [
        repository_root,
        current_branch,
        current_commit_hash,
        current_commit_short_hash,
        current_commit_message,
        status_short,
        status_porcelain,
        tracked_file_count,
        recent_commits,
        remotes,
    ]:
        if not command_result["success"] and command_result["stderr"]:
            git_info["errors"].append(f"{command_result['command']}: {command_result['stderr']}")

    return git_info


def build_report_purpose() -> str:
    return (
        "This report is intended to provide a fast but comprehensive understanding of the repository for a developer, reviewer, maintainer, or collaborator. "
        "It summarizes the project structure, key source files, generated artifacts, data files, dependencies, SQL assets, and Git repository state so that a reader can understand how the project is organized without manually opening every file."
    )


def build_project_overview(
    summary: dict,
    dependencies: list[str],
    python_files: list[Path],
    sql_files: list[Path],
    html_files: list[Path],
    csv_files: list[Path],
    database_files: list[Path],
) -> str:
    parts = []
    parts.append(
        f"This repository contains {summary['total_files']} files across {summary['total_directories']} directories and is centered on a todo analytics workflow built with Python, SQLite, Pandas, and Plotly."
    )
    parts.append(
        f"The codebase includes {len(python_files)} Python source files, {len(sql_files)} SQL files, {len(html_files)} HTML output files, {len(csv_files)} comma-separated data files, and {len(database_files)} SQLite database files."
    )
    if dependencies:
        parts.append(f"The declared runtime dependencies are: {', '.join(dependencies)}.")
    return " ".join(parts)


def build_architecture_summary(
    python_files: list[Path],
    sql_files: list[Path],
    html_files: list[Path],
    csv_files: list[Path],
    database_files: list[Path],
) -> str:
    parts = []

    parts.append(
        "The project is organized around four main layers: sample data generation, analytical querying, visualization output, and repository documentation."
    )

    if python_files:
        parts.append(
            "At the application layer, the Python scripts are responsible for creating demo todo records, storing them in SQLite, querying the dataset, calculating metrics, generating Plotly visualizations, and producing a standalone project report."
        )

    if sql_files:
        parts.append(
            "The SQL layer captures the core analytical queries in a reusable form, which helps separate reporting logic from the Python execution flow."
        )

    if database_files or csv_files:
        parts.append(
            "The data layer combines a local SQLite database with a comma-separated sample export, making it possible to inspect both the persisted relational dataset and a flat-file representation of the same domain."
        )

    if html_files:
        parts.append(
            "The output layer consists of generated HTML charts and Markdown summaries, which turn raw todo records into readable analytics artifacts."
        )

    parts.append(
        "Taken together, the repository functions as a compact analytics case study: a seeded todo domain is stored in SQLite, processed with Pandas, visualized with Plotly, and documented through both hand-written and generated project-level documentation."
    )

    return " ".join(parts)


def build_reproduction_section(dependencies: list[str]) -> str:
    dependency_lines = "\n".join(f"- `{dependency}`" for dependency in dependencies) if dependencies else "- No dependencies detected in `requirements.txt`."

    return "\n".join([
        "## How to reproduce this state",
        "",
        "The following steps describe how to reproduce the current repository state and regenerate the analytics outputs and project report on a fresh machine.",
        "",
        "### 1. Clone the repository",
        "",
        "```bash",
        "git clone https://github.com/antoniooreany/todo-insights-dashboard.git",
        "cd todo-insights-dashboard",
        "```",
        "",
        "### 2. Create and activate a virtual environment",
        "",
        "#### Windows PowerShell",
        "",
        "```powershell",
        "python -m venv .venv",
        ".\\.venv\\Scripts\\Activate.ps1",
        "```",
        "",
        "#### Linux / macOS",
        "",
        "```bash",
        "python -m venv .venv",
        "source .venv/bin/activate",
        "```",
        "",
        "### 3. Install dependencies",
        "",
        "```bash",
        "pip install -r requirements.txt",
        "```",
        "",
        "This installs the core runtime libraries used by the project:",
        "",
        dependency_lines,
        "",
        "### 4. Generate sample data",
        "",
        "```bash",
        "python scripts/seed_data.py",
        "```",
        "",
        "This step recreates the demo todo dataset and writes it to:",
        "",
        "- `data/todos.db` (SQLite database)",
        "- `data/sample_todos.csv` (CSV export)",
        "",
        "The records simulate tasks across categories such as work, study, personal, health, and admin, with fields like `title`, `category`, `priority`, `is_done`, `created_at`, `completed_at`, and `due_date`.",
        "",
        "### 5. Run the analytics script",
        "",
        "```bash",
        "python scripts/analyze_todos.py",
        "```",
        "",
        "This step:",
        "",
        "- reads `data/todos.db`",
        "- calculates summary metrics such as task count, completion rate, overdue tasks, and average completion time",
        "- writes a Markdown summary to `analysis_summary.md`",
        "- generates interactive Plotly charts and saves them as HTML files in `charts/`:",
        "  - `charts/created_over_time.html`",
        "  - `charts/completed_over_time.html`",
        "  - `charts/tasks_by_category.html`",
        "",
        "### 6. Generate the project report",
        "",
        "```bash",
        "python scripts/generate_project_report.py",
        "```",
        "",
        "This step scans the repository and produces a development-oriented report that:",
        "",
        "- explains the purpose of the report",
        "- summarizes the project at a high level",
        "- describes the architecture layers (data generation, SQL, analytics, visualization, documentation)",
        "- lists file types, sizes, and the largest files",
        "- shows the full repository tree (excluding non-essential directories such as `.venv`, `.git`, caches, and `.project-report`)",
        "- analyzes Python source files, imported modules, functions, and classes",
        "- summarizes SQL assets and their statement types",
        "- previews important files, including `README.md`, `analysis_summary.md`, Python scripts, SQL queries, and data files",
        "- captures Git metadata such as current branch, latest commit, remotes, tracked file count, and working tree status",
        "",
        "The script writes two outputs to `.project-report/`:",
        "",
        "- a human-readable Markdown report: `PROJECT_REPORT_YYYY-MM-DD_HH-MM-SS.md`",
        "- a machine-readable JSON report: `project-report_YYYY-MM-DD_HH-MM-SS.json`",
        "",
        "Together, these steps regenerate the current analytics artifacts and the repository report, making it possible to reproduce the state described in this document on another machine.",
    ])


def main() -> None:
    project_path = Path(".").resolve()
    output_directory = project_path / ".project-report"
    output_directory.mkdir(exist_ok=True)

    report_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print("Scanning project structure and files...")

    all_files: list[Path] = []
    all_directories: list[Path] = []
    extension_sizes: defaultdict[str, int] = defaultdict(int)
    extension_counts: Counter[str] = Counter()

    for current_root, directory_names, file_names in os.walk(project_path, topdown=True):
        directory_names[:] = [name for name in directory_names if not is_excluded_directory(name)]
        current_root_path = Path(current_root)

        for directory_name in directory_names:
            all_directories.append(current_root_path / directory_name)

        for file_name in file_names:
            file_path = current_root_path / file_name
            all_files.append(file_path)
            extension = file_path.suffix if file_path.suffix else "[no extension]"
            extension_counts[extension] += 1
            try:
                extension_sizes[extension] += file_path.stat().st_size
            except OSError:
                pass

    print("Preparing file statistics...")

    extension_statistics = [
        {
            "extension": extension,
            "count": extension_counts[extension],
            "total_size_bytes": extension_sizes[extension],
        }
        for extension, _ in extension_counts.most_common()
    ]

    largest_files = sorted(
        all_files,
        key=lambda path: path.stat().st_size if path.exists() else 0,
        reverse=True,
    )[:LARGEST_FILES_LIMIT]

    important_files = sorted(
        [
            path
            for path in all_files
            if path.name in IMPORTANT_FILE_NAMES or path.suffix.lower() in IMPORTANT_EXTENSIONS
        ],
        key=lambda path: str(path).lower(),
    )

    print("Analyzing source files, dependencies, SQL files, and repository metadata...")

    requirements_file = project_path / "requirements.txt"
    readme_file = project_path / "README.md"

    dependencies = parse_requirements(requirements_file)

    python_files = sorted([path for path in all_files if path.suffix.lower() == ".py"], key=lambda path: str(path).lower())
    sql_files = sorted([path for path in all_files if path.suffix.lower() == ".sql"], key=lambda path: str(path).lower())
    markdown_files = sorted([path for path in all_files if path.suffix.lower() == ".md"], key=lambda path: str(path).lower())
    html_files = sorted([path for path in all_files if path.suffix.lower() == ".html"], key=lambda path: str(path).lower())
    csv_files = sorted([path for path in all_files if path.suffix.lower() == ".csv"], key=lambda path: str(path).lower())
    database_files = sorted([path for path in all_files if path.suffix.lower() in {".db", ".sqlite3"}], key=lambda path: str(path).lower())

    python_file_analysis = []
    all_imported_modules = set()

    for python_file in python_files:
        parsed = parse_python_imports(python_file)
        all_imported_modules.update(parsed["imports"])
        all_imported_modules.update(parsed["import_from_modules"])
        try:
            stat = python_file.stat()
            size_bytes = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
        except OSError:
            size_bytes = 0
            modified = "unknown"
        python_file_analysis.append(
            {
                "path": relative_path(python_file, project_path),
                "size_bytes": size_bytes,
                "last_modified": modified,
                "imports": parsed["imports"],
                "import_from_modules": parsed["import_from_modules"],
                "functions": parsed["functions"],
                "classes": parsed["classes"],
                "has_main_guard": parsed["has_main_guard"],
            }
        )

    sql_file_analysis = []
    for sql_file in sql_files:
        try:
            stat = sql_file.stat()
            size_bytes = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
        except OSError:
            size_bytes = 0
            modified = "unknown"
        sql_summary = summarize_sql_file(sql_file)
        sql_file_analysis.append(
            {
                "path": relative_path(sql_file, project_path),
                "size_bytes": size_bytes,
                "last_modified": modified,
                "statement_summary": sql_summary,
            }
        )

    important_file_previews = []
    for path in important_files[:IMPORTANT_FILE_PREVIEW_LIMIT]:
        try:
            stat = path.stat()
            size_bytes = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
        except OSError:
            size_bytes = 0
            modified = "unknown"
        important_file_previews.append(
            {
                "path": relative_path(path, project_path),
                "file_type": classify_file(path),
                "size_bytes": size_bytes,
                "last_modified": modified,
                "preview": read_text_preview(path),
            }
        )

    git_information = collect_git_information(project_path)

    print("Building project tree and final report...")

    total_size_bytes = 0
    for path in all_files:
        try:
            total_size_bytes += path.stat().st_size
        except OSError:
            pass

    summary = {
        "total_directories": len(all_directories),
        "total_files": len(all_files),
        "total_size_bytes": total_size_bytes,
        "python_file_count": len(python_files),
        "sql_file_count": len(sql_files),
        "markdown_file_count": len(markdown_files),
        "html_file_count": len(html_files),
        "csv_file_count": len(csv_files),
        "database_file_count": len(database_files),
    }

    report_purpose = build_report_purpose()
    project_tree = build_project_tree(project_path)
    project_overview = build_project_overview(summary, dependencies, python_files, sql_files, html_files, csv_files, database_files)
    architecture_summary = build_architecture_summary(python_files, sql_files, html_files, csv_files, database_files)
    reproduction_section = build_reproduction_section(dependencies)

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "report_timestamp": report_timestamp,
        "project_path": str(project_path),
        "excluded_directories": sorted(EXCLUDED_DIRECTORIES),
        "report_purpose": report_purpose,
        "project_overview": project_overview,
        "architecture_summary": architecture_summary,
        "reproduction_section": reproduction_section,
        "summary": summary,
        "git_information": git_information,
        "dependencies_from_requirements": dependencies,
        "imported_python_modules": sorted(all_imported_modules),
        "project_tree": project_tree,
        "extension_statistics": extension_statistics,
        "largest_files": [
            {
                "path": relative_path(path, project_path),
                "size_bytes": path.stat().st_size if path.exists() else 0,
                "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if path.exists() else "unknown",
                "file_type": classify_file(path),
            }
            for path in largest_files
        ],
        "repository_artifacts": {
            "python_files": [relative_path(path, project_path) for path in python_files],
            "sql_files": [relative_path(path, project_path) for path in sql_files],
            "markdown_files": [relative_path(path, project_path) for path in markdown_files],
            "html_files": [relative_path(path, project_path) for path in html_files],
            "csv_files": [relative_path(path, project_path) for path in csv_files],
            "database_files": [relative_path(path, project_path) for path in database_files],
        },
        "python_file_analysis": python_file_analysis,
        "sql_file_analysis": sql_file_analysis,
        "important_file_previews": important_file_previews,
        "readme_preview": read_text_preview(readme_file) if readme_file.exists() else "[README not found]",
    }

    json_output_path = output_directory / f"project-report_{report_timestamp}.json"
    json_output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    extension_rows = "\n".join(f"| {item['extension']} | {item['count']} | {item['total_size_bytes']} |" for item in extension_statistics)
    largest_file_rows = "\n".join(
        f"| {item['path']} | {item['file_type']} | {item['size_bytes']} | {item['last_modified'].replace('T', ' ')} |"
        for item in report["largest_files"]
    )
    dependency_lines = "\n".join(f"- {dependency}" for dependency in dependencies) if dependencies else "- No requirements.txt dependencies found"
    imported_module_lines = "\n".join(f"- {module}" for module in report["imported_python_modules"]) if report["imported_python_modules"] else "- No imports detected"
    repository_artifact_lines = "\n".join([
        f"- Python source files: {len(python_files)}",
        f"- SQL files: {len(sql_files)}",
        f"- Markdown files: {len(markdown_files)}",
        f"- HTML files: {len(html_files)}",
        f"- Comma-separated data files: {len(csv_files)}",
        f"- Database files: {len(database_files)}",
    ])

    python_analysis_sections = "\n\n".join(
        "\n".join([
            f"### {item['path']}",
            f"- File size: {item['size_bytes']} bytes",
            f"- Last modified: {item['last_modified']}",
            f"- Has main guard: {item['has_main_guard']}",
            f"- Imported modules: {', '.join(item['imports']) if item['imports'] else 'None'}",
            f"- Imported modules via from-import: {', '.join(item['import_from_modules']) if item['import_from_modules'] else 'None'}",
            f"- Functions: {', '.join(item['functions']) if item['functions'] else 'None'}",
            f"- Classes: {', '.join(item['classes']) if item['classes'] else 'None'}",
        ])
        for item in python_file_analysis
    ) or "No Python files found."

    sql_analysis_sections = "\n\n".join(
        "\n".join([
            f"### {item['path']}",
            f"- File size: {item['size_bytes']} bytes",
            f"- Last modified: {item['last_modified']}",
            f"- SELECT statements detected: {item['statement_summary']['select_count']}",
            f"- INSERT statements detected: {item['statement_summary']['insert_count']}",
            f"- UPDATE statements detected: {item['statement_summary']['update_count']}",
            f"- DELETE statements detected: {item['statement_summary']['delete_count']}",
            f"- CREATE statements detected: {item['statement_summary']['create_count']}",
        ])
        for item in sql_file_analysis
    ) or "No SQL files found."

    important_file_preview_sections = "\n\n".join(
        "\n".join([
            f"## {item['path']}",
            f"- File type: {item['file_type']}",
            f"- File size: {item['size_bytes']} bytes",
            f"- Last modified: {item['last_modified']}",
            "",
            "```text",
            item["preview"],
            "```",
        ])
        for item in report["important_file_previews"]
    )

    if git_information["git_available"] and git_information["inside_git_repository"]:
        git_summary_lines = [
            f"- Git available: {git_information['git_available']}",
            f"- Inside Git repository: {git_information['inside_git_repository']}",
            f"- Repository root: {git_information['repository_root'] or 'Unknown'}",
            f"- Current branch: {git_information['current_branch'] or 'Unknown'}",
            f"- Current commit hash: {git_information['current_commit_hash'] or 'Unknown'}",
            f"- Current short commit hash: {git_information['current_commit_short_hash'] or 'Unknown'}",
            f"- Current commit message: {git_information['current_commit_message'] or 'Unknown'}",
            f"- Tracked file count: {git_information['tracked_file_count'] if git_information['tracked_file_count'] is not None else 'Unknown'}",
        ]
    else:
        git_summary_lines = [
            f"- Git available: {git_information['git_available']}",
            f"- Inside Git repository: {git_information['inside_git_repository']}",
        ]
        if git_information["errors"]:
            git_summary_lines.extend([f"- Error: {error}" for error in git_information["errors"]])

    recent_commit_lines = "\n".join(f"- {line}" for line in git_information["recent_commits"]) if git_information["recent_commits"] else "- No commit history available"
    remote_lines = git_information["remotes"] if git_information["remotes"] else "No Git remotes configured"
    git_status_short_block = git_information["working_tree_status_short"] if git_information["working_tree_status_short"] else "Working tree is clean"
    git_status_porcelain_block = git_information["working_tree_status_porcelain"] if git_information["working_tree_status_porcelain"] else "Working tree is clean"

    markdown_report = "\n".join([
        "# Project Report",
        "",
        f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- Report timestamp: {report_timestamp}",
        f"- Project path: {project_path}",
        f"- Excluded directories: {', '.join(sorted(EXCLUDED_DIRECTORIES))}",
        "",
        "## Report Purpose",
        "",
        report_purpose,
        "",
        "## Project Overview",
        "",
        project_overview,
        "",
        "## Architecture Summary",
        "",
        architecture_summary,
        "",
        "## Project Summary",
        "",
        f"- Total directories: {report['summary']['total_directories']}",
        f"- Total files: {report['summary']['total_files']}",
        f"- Total size in bytes: {report['summary']['total_size_bytes']}",
        f"- Python source files: {report['summary']['python_file_count']}",
        f"- SQL files: {report['summary']['sql_file_count']}",
        f"- Markdown files: {report['summary']['markdown_file_count']}",
        f"- HTML files: {report['summary']['html_file_count']}",
        f"- Comma-separated data files: {report['summary']['csv_file_count']}",
        f"- Database files: {report['summary']['database_file_count']}",
        "",
        "## Git Repository Information",
        "",
        *git_summary_lines,
        "",
        "### Git Remotes",
        "",
        "```text",
        remote_lines,
        "```",
        "",
        "### Recent Commits",
        "",
        recent_commit_lines,
        "",
        "### Git Status Short",
        "",
        "```text",
        git_status_short_block,
        "```",
        "",
        "### Git Status Porcelain",
        "",
        "```text",
        git_status_porcelain_block,
        "```",
        "",
        "## Repository Structure",
        "",
        "```text",
        "\n".join(project_tree),
        "```",
        "",
        "## Repository Artifact Summary",
        "",
        repository_artifact_lines,
        "",
        "## Dependency List",
        "",
        dependency_lines,
        "",
        "## Imported Python Modules",
        "",
        imported_module_lines,
        "",
        "## File Type Statistics",
        "",
        "| Extension | Count | Total size in bytes |",
        "|---|---:|---:|",
        extension_rows,
        "",
        "## Largest Files",
        "",
        "| Path | File type | Size in bytes | Last modified |",
        "|---|---|---:|---|",
        largest_file_rows,
        "",
        "## README Preview",
        "",
        "```text",
        report["readme_preview"],
        "```",
        "",
        reproduction_section,
        "",
        "## Python Source File Analysis",
        "",
        python_analysis_sections,
        "",
        "## SQL File Analysis",
        "",
        sql_analysis_sections,
        "",
        "## Important File Previews",
        "",
        important_file_preview_sections,
        "",
    ])

    markdown_output_path = output_directory / f"PROJECT_REPORT_{report_timestamp}.md"
    markdown_output_path.write_text(markdown_report, encoding="utf-8")

    print("Done.")
    print(f"Created: {markdown_output_path}")
    print(f"Created: {json_output_path}")


if __name__ == "__main__":
    main()