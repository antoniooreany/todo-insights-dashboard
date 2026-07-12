from pathlib import Path


def test_analyze_todos_script_exists():
    assert Path("scripts/analyze_todos.py").exists()


def test_sql_queries_file_exists():
    assert Path("sql/queries.sql").exists()


def test_data_directory_exists():
    assert Path("data").exists()
