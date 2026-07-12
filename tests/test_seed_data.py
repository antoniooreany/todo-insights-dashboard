from scripts.seed_data import build_rows, CATEGORIES, PRIORITIES


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
