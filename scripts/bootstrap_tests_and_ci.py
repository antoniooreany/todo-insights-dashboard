from __future__ import annotations

from pathlib import Path


TEST_SEED_DATA = """from scripts.seed_data import build_rows, CATEGORIES, PRIORITIES


def test_build_rows_returns_expected_number_of_rows():
    rows = build_rows(20)
    assert len(rows) == 20


def test_build_rows_use_known_categories_and_priorities():
    rows = build_rows(30)
    for row in rows:
        assert row["category"] in CATEGORIES
        assert row["priority"] in PRIORITIES


def test_build_rows_have_required_fields():
    rows = build_rows(10)
    required_fields = {
        "title",
        "description",
        "category",
        "priority",
        "is_done",
        "created_at",
        "completed_at",
        "due_date",
    }

    for row in rows:
        assert required_fields.issubset(row.keys())
        assert row["is_done"] in (0, 1)
"""

TEST_GENERATE_PROJECT_REPORT = """from pathlib import Path
from scripts.generate_project_report import (
    classify_file,
    is_excluded_directory,
    parse_requirements,
)


def test_is_excluded_directory_recognizes_known_directories():
    assert is_excluded_directory(".venv") is True
    assert is_excluded_directory(".project-report") is True
    assert is_excluded_directory("scripts") is False


def test_classify_file_detects_common_file_types():
    assert classify_file(Path("file.py")) == "Python source file"
    assert classify_file(Path("file.sql")) == "SQL file"
    assert classify_file(Path("file.md")) == "Markdown documentation"
    assert classify_file(Path("file.db")) == "SQLite database file"


def test_parse_requirements_reads_dependencies(tmp_path):
    req = tmp_path / "requirements.txt"
    req.write_text("pandas>=2.2.0\\nplotly>=5.24.0\\n# comment\\n", encoding="utf-8")

    result = parse_requirements(req)

    assert result == ["pandas>=2.2.0", "plotly>=5.24.0"]
"""

TEST_ANALYZE_TODOS = """from pathlib import Path


def test_analyze_todos_script_exists():
    assert Path("scripts/analyze_todos.py").exists()


def test_sql_queries_file_exists():
    assert Path("sql/queries.sql").exists()


def test_data_directory_exists():
    assert Path("data").exists()
"""

CI_YAML = """name: Python CI

on:
  push:
    branches:
      - develop
      - main
      - "feature/**"
  pull_request:
    branches:
      - develop
      - main

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.11"]

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Run tests
        run: python -m pytest
"""

README_TESTING_SECTION = """## Testing

Run tests locally with:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```
"""

README_CI_SECTION = """## Continuous integration

This repository uses GitHub Actions to run automated tests on:
- pushes to feature, develop, and main branches
- pull requests targeting develop and main

The CI workflow installs development dependencies from `requirements-dev.txt` and runs:

```bash
python -m pytest
```
"""


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_file_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    ensure_directory(path.parent)
    path.write_text(content, encoding="utf-8")
    return True


def ensure_file_content(path: Path, content: str) -> bool:
    ensure_directory(path.parent)
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def ensure_init_file(path: Path) -> bool:
    if path.exists():
        return False
    ensure_directory(path.parent)
    path.write_text("", encoding="utf-8")
    return True


def ensure_requirements_dev(path: Path) -> bool:
    desired_lines = [
        "-r requirements.txt",
        "pytest>=8.0.0",
    ]
    desired_text = "\n".join(desired_lines) + "\n"

    if not path.exists():
        path.write_text(desired_text, encoding="utf-8")
        return True

    current_lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    changed = False
    for line in desired_lines:
        if line not in current_lines:
            current_lines.append(line)
            changed = True

    if changed:
        path.write_text("\n".join(current_lines) + "\n", encoding="utf-8")

    return changed


def ensure_requirements_runtime_clean(path: Path) -> bool:
    if not path.exists():
        return False

    lines = path.read_text(encoding="utf-8").splitlines()
    filtered = [line for line in lines if not line.strip().startswith("pytest")]
    new_text = "\n".join(filtered).rstrip() + "\n"

    old_text = path.read_text(encoding="utf-8")
    if old_text == new_text:
        return False

    path.write_text(new_text, encoding="utf-8")
    return True


def append_readme_section_if_missing(readme_text: str, heading: str, section_text: str) -> tuple[str, bool]:
    if heading in readme_text:
        return readme_text, False

    if not readme_text.endswith("\n"):
        readme_text += "\n"

    readme_text += "\n" + section_text.strip() + "\n"
    return readme_text, True


def ensure_readme_sections(path: Path) -> bool:
    if not path.exists():
        initial_text = "# Todo Insights Dashboard\n\n" + README_TESTING_SECTION + "\n" + README_CI_SECTION
        path.write_text(initial_text, encoding="utf-8")
        return True

    text = path.read_text(encoding="utf-8")
    changed = False

    text, updated_testing = append_readme_section_if_missing(text, "## Testing", README_TESTING_SECTION)
    text, updated_ci = append_readme_section_if_missing(text, "## Continuous integration", README_CI_SECTION)

    changed = updated_testing or updated_ci

    if changed:
        path.write_text(text, encoding="utf-8")

    return changed


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    created_or_updated: list[str] = []

    tests_dir = root / "tests"
    scripts_dir = root / "scripts"
    github_workflows_dir = root / ".github" / "workflows"

    ensure_directory(tests_dir)
    ensure_directory(scripts_dir)
    ensure_directory(github_workflows_dir)

    paths_and_contents = [
        (tests_dir / "test_seed_data.py", TEST_SEED_DATA),
        (tests_dir / "test_generate_project_report.py", TEST_GENERATE_PROJECT_REPORT),
        (tests_dir / "test_analyze_todos.py", TEST_ANALYZE_TODOS),
    ]

    for path, content in paths_and_contents:
        if write_file_if_missing(path, content):
            created_or_updated.append(f"Created {path.relative_to(root)}")

    if ensure_init_file(scripts_dir / "__init__.py"):
        created_or_updated.append("Created scripts/__init__.py")

    if ensure_init_file(tests_dir / "__init__.py"):
        created_or_updated.append("Created tests/__init__.py")

    if ensure_file_content(github_workflows_dir / "ci.yml", CI_YAML):
        created_or_updated.append("Created/updated .github/workflows/ci.yml")

    if ensure_requirements_dev(root / "requirements-dev.txt"):
        created_or_updated.append("Created/updated requirements-dev.txt")

    if ensure_requirements_runtime_clean(root / "requirements.txt"):
        created_or_updated.append("Updated requirements.txt to keep runtime dependencies only")

    if ensure_readme_sections(root / "README.md"):
        created_or_updated.append("Updated README.md with testing and CI sections")

    if not created_or_updated:
        print("No changes were necessary.")
        return

    print("Applied changes:")
    for item in created_or_updated:
        print(f"- {item}")

    print("\\nNext steps:")
    print("1. python -m pip install -r requirements-dev.txt")
    print("2. python -m pytest")
    print("3. git add .")
    print('4. git commit -m "Add pytest scaffolding and GitHub Actions CI"')


if __name__ == "__main__":
    main()