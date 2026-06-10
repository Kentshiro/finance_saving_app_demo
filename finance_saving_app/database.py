"""SQLite persistence layer for the budgeting tool.

This module isolates all database access behind :class:`BudgetDatabase` so the
UI layer never embeds raw SQL. The data shapes it consumes and returns match
the in-memory structures used by ``ui.BudgetingTool``:

* ``user_details``    -> ``{user_id: {"name", "wage", "wage_type", "expenses"}}``
  where ``expenses`` is ``{expense_name: value_as_str}``.
* ``shared_expenses`` -> ``{expense_name: value_as_str}``.
"""

import sqlite3

from pathlib import Path

_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    income REAL,
    income_type INTEGER
)
"""

_CREATE_EXPENSES = """
CREATE TABLE IF NOT EXISTS expenses (
    user_id TEXT,
    expense_name TEXT,
    expense_value REAL,
    PRIMARY KEY(user_id, expense_name),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
"""

_CREATE_SHARED_EXPENSES = """
CREATE TABLE IF NOT EXISTS shared_expenses (
    expense_name TEXT PRIMARY KEY,
    expense_value REAL
)
"""


def default_db_path() -> Path:
    """Return the default location of the SQLite database file."""
    return Path(__file__).resolve().parent / "data" / "data.db"


def _coerce_float(value, default=0.0) -> float:
    """Best-effort conversion to float, falling back to ``default``."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class BudgetDatabase:
    """Read/write access to the budgeting tool's SQLite store."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path) if db_path else default_db_path()

    def load(self) -> tuple[dict, dict]:
        """Load saved users and shared expenses.

        Returns:
            tuple(dict, dict): ``(user_details, shared_expenses)``. Either may be
            empty if nothing has been saved yet (e.g. a fresh database). The
            caller is responsible for substituting defaults.
        """
        if not self.db_path.exists():
            return {}, {}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            if not cursor.fetchone():
                return {}, {}

            user_details = {}
            cursor.execute("SELECT user_id, name, income, income_type FROM users")
            for user_id, name, income, income_type in cursor.fetchall():
                user_details[user_id] = {
                    "name": name,
                    "wage": income,
                    "wage_type": bool(int(income_type)),
                    "expenses": {},
                }
                cursor.execute(
                    "SELECT expense_name, expense_value FROM expenses WHERE user_id=?",
                    (user_id,),
                )
                user_details[user_id]["expenses"] = {
                    exp_name: str(value) for exp_name, value in cursor.fetchall()
                }

            cursor.execute("SELECT expense_name, expense_value FROM shared_expenses")
            shared_expenses = {name: str(value) for name, value in cursor.fetchall()}

        return user_details, shared_expenses

    def save(self, user_details: dict, shared_expenses: dict) -> Path:
        """Persist users, their expenses, and shared expenses.

        Existing rows are upserted and rows no longer present in the supplied
        data are removed, keeping the database in sync with the UI state.

        Args:
            user_details: Compiled user data with ``expenses`` as name->str maps.
            shared_expenses: Shared expense name->str map.

        Returns:
            Path: The path of the database that was written.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(_CREATE_USERS)
            cursor.execute(_CREATE_EXPENSES)
            cursor.execute(_CREATE_SHARED_EXPENSES)

            for user_id, details in user_details.items():
                cursor.execute(
                    """
                    INSERT INTO users (user_id, name, income, income_type)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        name = excluded.name,
                        income = excluded.income,
                        income_type = excluded.income_type
                    """,
                    (
                        user_id,
                        details.get("name", ""),
                        details.get("wage", 0),
                        int(details.get("wage_type", 0)),
                    ),
                )

                expenses = details.get("expenses", {})
                self._sync_user_expenses(cursor, user_id, expenses)
                for exp_name, exp_value in expenses.items():
                    cursor.execute(
                        """
                        INSERT INTO expenses (user_id, expense_name, expense_value)
                        VALUES (?, ?, ?)
                        ON CONFLICT(user_id, expense_name)
                        DO UPDATE SET expense_value = excluded.expense_value
                        """,
                        (user_id, exp_name, _coerce_float(exp_value)),
                    )

            self._sync_shared_expenses(cursor, shared_expenses)
            for exp_name, exp_value in shared_expenses.items():
                cursor.execute(
                    """
                    INSERT INTO shared_expenses (expense_name, expense_value)
                    VALUES (?, ?)
                    ON CONFLICT(expense_name)
                    DO UPDATE SET expense_value = excluded.expense_value
                    """,
                    (exp_name, _coerce_float(exp_value)),
                )

            conn.commit()

        return self.db_path

    @staticmethod
    def _sync_user_expenses(cursor, user_id, current_expenses) -> None:
        """Delete a user's stored expenses that are no longer present."""
        cursor.execute("SELECT expense_name FROM expenses WHERE user_id = ?", (user_id,))
        stored = {row[0] for row in cursor.fetchall()}
        for expense in stored - set(current_expenses):
            cursor.execute(
                "DELETE FROM expenses WHERE user_id = ? AND expense_name = ?",
                (user_id, expense),
            )

    @staticmethod
    def _sync_shared_expenses(cursor, current_shared_expenses) -> None:
        """Delete stored shared expenses that are no longer present."""
        cursor.execute("SELECT expense_name FROM shared_expenses")
        stored = {row[0] for row in cursor.fetchall()}
        for expense in stored - set(current_shared_expenses):
            cursor.execute(
                "DELETE FROM shared_expenses WHERE expense_name = ?", (expense,)
            )
