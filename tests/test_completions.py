# tests/test_completions.py
from datetime import datetime


def test_daily_completions_cover_four_weeks(four_weeks_completions):
    """
    Daily habits should have one completion per day over four weeks or 28 times.
    """
    # Select all completion events for a daily habit (Drink Water)
    daily = [c for c in four_weeks_completions if c["habit_id"] == 1]

    # Four weeks of daily tracking should result in 28 entries
    assert len(daily) == 28

    # The last completion should fall in early February
    last_timestamp = daily[-1]["completed_at"]
    assert last_timestamp.startswith("2025-02")


def test_weekly_completions_are_spaced_correctly(four_weeks_completions):
    """
    Weekly habits should be completed exactly once per week.
    """
    # Select completion events for a weekly habit (Call Family)
    weekly = [c for c in four_weeks_completions if c["habit_id"] == 4]

    # Four weeks → four completion events
    assert len(weekly) == 4

    # Convert timestamps to datetime objects for comparison
    times = [datetime.fromisoformat(c["completed_at"]) for c in weekly]

    # Each completion should be exactly 7 days after the previous one
    for earlier, later in zip(times, times[1:]):
        delta_days = (later - earlier).days
        assert delta_days == 7
