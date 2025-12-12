"""
Pytest fixtures shared across the test suite.

The fixtures provide predefined habit data and completion history
for four weeks of tracking and are used to test streak logic and
analytics functionality.

"""

from datetime import date, timedelta, datetime
import pytest


@pytest.fixture
def four_weeks_habits():
    """
    Return five predefined habits with four weeks or 28 days of tracking data.

    Included are:
    - Three daily habits
    - Two weekly habits
    - Precomputed streak values
    - Last completion dates consistent with four weeks of activity

    """
    start = date(2025, 1, 6)  # Monday used as a start date

    return [
        {
            "id": 1,
            "user_id": 1,
            "name": "Drink Water",
            "description": "8 glasses",
            "goal": "Hydration",
            "start_date": start.isoformat(),
            "periodicity": "daily",
            "reminder": "09:00",
            "completed": 1,
            "streak": 28,
            "last_completed_date": (start + timedelta(days=27)).isoformat(),
        },
        {
            "id": 2,
            "user_id": 1,
            "name": "Read",
            "description": "Read 10 pages",
            "goal": "Learning",
            "start_date": start.isoformat(),
            "periodicity": "daily",
            "reminder": "20:30",
            "completed": 1,
            "streak": 21,
            "last_completed_date": (start + timedelta(days=20)).isoformat(),
        },
        {
            "id": 3,
            "user_id": 1,
            "name": "Meditate",
            "description": "5 minutes breathing",
            "goal": "Mindfulness",
            "start_date": start.isoformat(),
            "periodicity": "daily",
            "reminder": None,
            "completed": 1,
            "streak": 14,
            "last_completed_date": (start + timedelta(days=13)).isoformat(),
        },
        {
            "id": 4,
            "user_id": 1,
            "name": "Call Family",
            "description": "Weekly call",
            "goal": "Relationships",
            "start_date": start.isoformat(),
            "periodicity": "weekly",
            "reminder": None,
            "completed": 1,
            "streak": 4,
            "last_completed_date": (start + timedelta(weeks=3)).isoformat(),
        },
        {
            "id": 5,
            "user_id": 1,
            "name": "Budget Review",
            "description": "Review budget",
            "goal": "Finance",
            "start_date": start.isoformat(),
            "periodicity": "weekly",
            "reminder": "18:00",
            "completed": 1,
            "streak": 3,
            "last_completed_date": (start + timedelta(weeks=2)).isoformat(),
        },
    ]


@pytest.fixture
def four_weeks_completions():
    """
    Return detailed completion history for four weeks of tracking.

    This fixture simulates actual habit completion events with
    timestamps:
    - Daily habits (IDs 1–3) are completed every day for 28 days.
    - Weekly habits (IDs 4–5) are completed once per week for 4 weeks.

    Completion times are returned as ISO 8601 strings to match
    the database format used by the application.
    """
    start = datetime(2025, 1, 6, 9, 0)  # Monday used as a start date
    completions = []

    # Generate daily completions (28 consecutive days)
    for habit_id in (1, 2, 3):
        for day in range(28):
            completed_at = start + timedelta(days=day, hours=habit_id)
            completions.append(
                {
                    "habit_id": habit_id,
                    "completed_at": completed_at.isoformat(timespec="minutes"),
                }
            )

    # Generate weekly completions (once per week for 4 weeks)
    for habit_id in (4, 5):
        for week in range(4):
            completed_at = start + timedelta(weeks=week, hours=habit_id)
            completions.append(
                {
                    "habit_id": habit_id,
                    "completed_at": completed_at.isoformat(timespec="minutes"),
                }
            )

    return completions

