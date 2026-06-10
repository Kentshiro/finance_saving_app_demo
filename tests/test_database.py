"""Tests for the SQLite persistence layer in ``finance_saving_app.database``.

These run headless against a temporary database file — no Qt dependency.
"""

from finance_saving_app.database import BudgetDatabase, default_db_path


def _make_db(tmp_path):
    return BudgetDatabase(tmp_path / "test.db")


def _user(name="Alice", wage=3000, wage_type=True, expenses=None):
    return {"name": name, "wage": wage, "wage_type": wage_type, "expenses": expenses or {}}


class TestLoad:
    def test_missing_database_returns_empty(self, tmp_path):
        db = _make_db(tmp_path)
        assert db.load() == ({}, {})

    def test_roundtrip_preserves_users_and_expenses(self, tmp_path):
        db = _make_db(tmp_path)
        users = {"01": _user(name="Alice", wage=3000, expenses={"Food": "200"})}
        shared = {"Rent": "1250"}

        db.save(users, shared)
        loaded_users, loaded_shared = db.load()

        assert loaded_users["01"]["name"] == "Alice"
        assert loaded_users["01"]["wage"] == 3000
        assert loaded_users["01"]["wage_type"] is True
        # Values come back as strings, normalised through float storage.
        assert loaded_users["01"]["expenses"]["Food"] == "200.0"
        assert loaded_shared["Rent"] == "1250.0"

    def test_wage_type_false_roundtrips_as_bool(self, tmp_path):
        db = _make_db(tmp_path)
        db.save({"01": _user(wage_type=False)}, {})
        loaded_users, _ = db.load()
        assert loaded_users["01"]["wage_type"] is False


class TestSyncOnSave:
    def test_removes_orphaned_user_expense(self, tmp_path):
        db = _make_db(tmp_path)
        db.save({"01": _user(expenses={"Food": "200", "Gym": "50"})}, {})

        # Re-save without "Gym" -> it should be deleted from the DB.
        db.save({"01": _user(expenses={"Food": "200"})}, {})

        loaded_users, _ = db.load()
        assert set(loaded_users["01"]["expenses"]) == {"Food"}

    def test_removes_orphaned_shared_expense(self, tmp_path):
        db = _make_db(tmp_path)
        db.save({}, {"Rent": "1250", "Water": "17"})
        db.save({}, {"Rent": "1250"})

        _, loaded_shared = db.load()
        assert set(loaded_shared) == {"Rent"}


class TestCoercion:
    def test_non_numeric_expense_stored_as_zero(self, tmp_path):
        db = _make_db(tmp_path)
        db.save({"01": _user(expenses={"Food": "not-a-number"})}, {"Rent": ""})
        loaded_users, loaded_shared = db.load()
        assert loaded_users["01"]["expenses"]["Food"] == "0.0"
        assert loaded_shared["Rent"] == "0.0"


def test_default_db_path_points_at_data_dir():
    path = default_db_path()
    assert path.name == "data.db"
    assert path.parent.name == "data"
