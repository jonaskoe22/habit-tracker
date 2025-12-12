# tests/test_db.py
import os
import tempfile
from datetime import date

import pytest

from app.db.database import Database
from app.models.habit import Habit


def test_initialize_and_crud_cycle():
    """
    A complete database test.

    This test verifies that users and habits can be created,
    retrieved, updated, and stored correctly using SQLite.
    """
    with tempfile.TemporaryDirectory() as tmp:
        # Use a temporary database file so tests do not affect real data
        path = os.path.join(tmp, "habits.sqlite3")
        db = Database(path)
        db.initialize()

        # Create a user and ensure an ID is returned
        user_id = db.save_user("Jonas", "jonas@example.com")
        assert user_id > 0

        # Create a habit using the model and persist it via the database
        habit = Habit.from_form(
            "Drink Water",
            "8 glasses",
            "Hydration",
            "2025-08-01",
            periodicity="daily",
            reminder="09:00",
        )

        habit_id = db.save_habit(
            user_id=user_id,
            name=habit.name,
            description=habit.description,
            goal=habit.goal,
            start_date=habit.start_date.date().isoformat(),
            periodicity=habit.periodicity,
            reminder=habit.reminder.isoformat(timespec="minutes") if habit.reminder else None,
            completed=0,
            streak=0,
            last_completed_date=None,
        )

        # The habit should now appear when fetching habits for the user
        rows = db.fetch_habits_by_user(user_id)
        assert any(r["id"] == habit_id and r["name"] == "Drink Water" for r in rows)

        # Simulate checking off the habit on a specific date
        today = date(2025, 8, 24)
        habit.streak = 0
        habit.last_completed_date = None
        habit.check_off(on_date=today)

        # Persist the updated streak and completion date
        db.update_habit_progress(
            habit_id,
            completed=1,
            streak=habit.streak,
            last_completed_date=today.isoformat(),
        )

        # Reload the habit from the database and verify the updates
        rows = db.fetch_habits_by_user(user_id)
        row = next(r for r in rows if r["id"] == habit_id)

        assert row["completed"] == 1
        assert row["streak"] == 1
        assert row["last_completed_date"] == today.isoformat()


def test_unique_email_constraint():
    """
    The database should prevent duplicate user email addresses.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "habits.sqlite3")
        db = Database(path)
        db.initialize()

        # First insert should succeed
        db.save_user("A", "a@ex.com")

        # Second insert with the same email should fail
        with pytest.raises(Exception):
            db.save_user("B", "a@ex.com")
