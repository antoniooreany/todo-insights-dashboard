from __future__ import annotations

from datetime import date
from pathlib import Path


VERSION = "0.1.0"
RELEASE_DATE = "2026-07-12"
AUTHOR_NAME = "Antonio Oreany"
YEAR = str(date.today().year)

CHANGELOG_HEADER = """# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and the project follows a simple semantic versioning style.

## [Unreleased]

### Added

- Placeholder for upcoming features.

"""

CHANGELOG_RELEASE_SECTION = f"""## [{VERSION}] - {RELEASE_DATE}

### Added

- Seeded demo todo dataset in SQLite and CSV formats.
- Analytics script for summary metrics such as completion rate, overdue tasks, and average completion time.
- Plotly HTML charts for created tasks over time, completed tasks over time, and tasks by category.
- SQL query collection for reusable reporting logic.
- Project report generator for repository inspection and reproducibility.
- Basic pytest-based test scaffolding.
- GitHub Actions CI workflow for automated test execution.

### Changed

- Improved README documentation with clearer setup, usage, project reporting, testing, and CI instructions.
- Updated repository structure to support report generation and test automation.

### Fixed

- Improved local test execution by aligning the test package structure with Python imports.

"""

MIT_LICENSE = f"""MIT License

Copyright (c) {YEAR} {AUTHOR_NAME}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

RELEASE_TEMPLATE = f"""# Todo Insights Dashboard v{VERSION}

## Highlights

- seeded demo todo dataset in SQLite and CSV
- analytics script for core metrics and summaries
- Plotly charts for task trends and category distribution
- project report generator for repository inspection and reproducibility
- improved README documentation
- basic pytest tests
- GitHub Actions CI for automated test runs

## Scope

This release publishes the first complete portfolio-ready version of the project from `develop` to `main`.

## Included capabilities

- sample todo data generation
- SQLite-based analytics workflow
- SQL reporting queries
- Markdown analysis summary
- interactive HTML charts
- generated project report
- basic automated testing
- continuous integration
"""

README_METADATA_SECTION = """## Project metadata

This repository includes additional project metadata files for release and maintenance workflows:

- `CHANGELOG.md` for notable versioned changes
- `LICENSE` for repository licensing terms
- `.github/release-template.md` for GitHub release drafting
"""


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str) -> bool:
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


def ensure_changelog(path: Path) -> bool:
    if not path.exists():
        path.write_text(CHANGELOG_HEADER + CHANGELOG_RELEASE_SECTION, encoding="utf-8")
        return True

    text = path.read_text(encoding="utf-8")

    changed = False

    if "# Changelog" not in text:
        text = CHANGELOG_HEADER + "\n" + text
        changed = True

    if f"## [{VERSION}] - {RELEASE_DATE}" not in text:
        if "## [Unreleased]" in text:
            marker = "## [Unreleased]"
            insert_after = text.find(marker) + len(marker)
            remaining = text[insert_after:]
            text = text[:insert_after] + "\n\n### Added\n\n- Placeholder for upcoming features.\n\n" + CHANGELOG_RELEASE_SECTION + remaining
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += "\n" + CHANGELOG_RELEASE_SECTION
        changed = True

    if changed:
        path.write_text(text, encoding="utf-8")

    return changed


def ensure_readme_metadata_section(path: Path) -> bool:
    if not path.exists():
        path.write_text("# Todo Insights Dashboard\n\n" + README_METADATA_SECTION, encoding="utf-8")
        return True

    text = path.read_text(encoding="utf-8")
    if "## Project metadata" in text:
        return False

    if not text.endswith("\n"):
        text += "\n"
    text += "\n" + README_METADATA_SECTION
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    changelog_path = root / "CHANGELOG.md"
    license_path = root / "LICENSE"
    release_template_path = root / ".github" / "release-template.md"
    readme_path = root / "README.md"

    applied_changes: list[str] = []

    if ensure_changelog(changelog_path):
        applied_changes.append("Created/updated CHANGELOG.md")

    if write_if_missing(license_path, MIT_LICENSE):
        applied_changes.append("Created LICENSE")

    if ensure_file_content(release_template_path, RELEASE_TEMPLATE):
        applied_changes.append("Created/updated .github/release-template.md")

    if ensure_readme_metadata_section(readme_path):
        applied_changes.append("Updated README.md with project metadata section")

    if not applied_changes:
        print("No changes were necessary.")
        return

    print("Applied changes:")
    for item in applied_changes:
        print(f"- {item}")

    print("\nNext steps:")
    print("1. Review CHANGELOG.md, LICENSE, and .github/release-template.md")
    print("2. git add CHANGELOG.md LICENSE .github/release-template.md README.md scripts/bootstrap_release_docs.py")
    print('3. git commit -m "Add changelog, license, and release metadata"')


if __name__ == "__main__":
    main()