from pathlib import Path
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
    req.write_text("pandas>=2.2.0\nplotly>=5.24.0\n# comment\n", encoding="utf-8")

    result = parse_requirements(req)

    assert result == ["pandas>=2.2.0", "plotly>=5.24.0"]
