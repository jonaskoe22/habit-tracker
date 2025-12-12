# tests/test_analytics_api.py
from copy import deepcopy

from app.analysis.analyse import (
    list_all_habits,
    list_by_periodicity,
    longest_run_streak,
    longest_run_streak_for,
)


def test_list_all_habits_returns_all(four_weeks_habits):
    """
    All predefined habits should be returned when no filtering is applied.
    """
    views = list_all_habits(four_weeks_habits)

    # We expect exactly the five habits from the fixture
    assert len(views) == 5

    #Check: one known habit should be present
    assert any(v.name == "Drink Water" for v in views)


def test_list_by_periodicity_filters_correctly(four_weeks_habits):
    """
    Habits should be correctly grouped by their periodicity.
    """
    dailies = list_by_periodicity(four_weeks_habits, "daily")
    weeklies = list_by_periodicity(four_weeks_habits, "weekly")

    # Make sure both groups are present in the fixture
    assert dailies
    assert weeklies

    # Every returned habit must match the requested periodicity
    assert all(v.periodicity == "daily" for v in dailies)
    assert all(v.periodicity == "weekly" for v in weeklies)


def test_longest_run_streak_picks_max(four_weeks_habits):
    """
    The analytics function should return the habit with the highest streak.
    """
    # Work on a copy so the shared fixture is not modified
    rows = deepcopy(four_weeks_habits)

    # Assign increasing streak values so the last habit is the maximum
    for idx, row in enumerate(rows, start=1):
        row["streak"] = idx

    habit_id, streak = longest_run_streak(rows)

    # The habit with id=5 should now have the longest streak
    assert habit_id == 5
    assert streak == 5


def test_longest_run_streak_for_returns_value(four_weeks_habits):
    """
    Asking for a specific habit should return its streak value.
    """
    rows = deepcopy(four_weeks_habits)

    # Manually set a streak for one habit
    rows[0]["streak"] = 7

    result = longest_run_streak_for(rows, habit_id=rows[0]["id"])
    assert result == 7


def test_longest_run_streak_for_returns_zero_if_missin


def test_longest_run_streak_for_returns_zero_if_missing(four_weeks_habits):
    """If a habit id is not present in rows, the result should be 0."""
    result = longest_run_streak_for(four_weeks_habits, habit_id=9999)
    assert result == 0

