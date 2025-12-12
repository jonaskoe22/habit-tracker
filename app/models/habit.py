# app/models/habit.py
"""
Habit model with periodicity-aware streak logic.

A Habit represents one tracked activity and stores its progress state (streak, last completion date). 
The streak logicdepends on the habit's periodicity (daily / weekly / monthly).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Optional, Literal
from calendar import monthrange

Periodicity = Literal["daily", "weekly", "monthly"]


@dataclass
class Habit:
    """
    A habit with state needed for tracking progress.

    Attributes:
        name: Short name shown in the CLI.
        description: Longer description shown to the user.
        goal: The purpose of the habit.
        start_date: When the habit was created (stored as datetime).
        periodicity: How often the habit should be completed.
        reminder: Optional reminder time (HH:MM).
        completed: Whether the habit was completed in the latest recorded period.
        streak: Current run streak.
        last_completed_date: The date the habit was last checked off.
    """

    name: str
    description: str
    goal: str
    start_date: datetime
    periodicity: Periodicity = "daily"
    reminder: Optional[time] = None
    completed: bool = False
    streak: int = 0
    last_completed_date: Optional[date] = None

    def check_off(self, on_date: Optional[date] = None) -> None:
        """
        Mark the habit as completed on a given date and update the streak.

        Rules:
        - First completion always starts a streak at 1.
        - If the completion matches the expected next period the streak increments.
        - If the completion happens after the expected date the streak resets to 1.
        - If the completion happens in the same period the streak stays the same.
        """
        on_date = on_date or date.today()

        # If this is the first time the habit is completed, the streak is started.
        if self.last_completed_date is None:
            self.streak = 1
        else:
            expected = self._expected_next_date()

            # Expected is always defined here.
            if expected is not None and on_date == expected:
                self.streak += 1
            elif expected is not None and on_date > expected:
                # User missed at least one required period, so the streak resets.
                self.streak = 1
            else:
                # Same-day completion or “early” completion:
                # Record the completion, but do not increase the streak.
                pass

        self.completed = True
        self.last_completed_date = on_date

    def _expected_next_date(self) -> Optional[date]:
        """
        Calculate the next date that would continue the current streak.

        Returns:
            The date the next completion is expected,
            or None if there is no previous completion date.
        """
        if self.last_completed_date is None:
            return None

        if self.periodicity == "daily":
            return self.last_completed_date + timedelta(days=1)

        if self.periodicity == "weekly":
            return self.last_completed_date + timedelta(weeks=1)

        # Monthly: same day next month, but clamp to month-end if needed.
        year = self.last_completed_date.year
        month = self.last_completed_date.month + 1
        if month == 13:
            year += 1
            month = 1

        last_day = monthrange(year, month)[1]
        day = min(self.last_completed_date.day, last_day)
        return date(year, month, day)

    @classmethod
    def from_form(
        cls,
        name: str,
        description: str,
        goal: str,
        start_date: str,
        periodicity: Periodicity = "daily",
        reminder: Optional[str] = None,
    ) -> "Habit":
        """
        Create a Habit instance from CLI input strings.

        Args:
            name: Habit name.
            description: Habit description.
            goal: Goal/category.
            start_date: Date string in YYYY-MM-DD format.
            periodicity: daily / weekly / monthly.
            reminder: Optional time string in HH:MM format.

        Raises:
            ValueError: If date/time formats are invalid.
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        reminder_time: Optional[time] = None
        if reminder:
            reminder_time = datetime.strptime(reminder, "%H:%M").time()

        if periodicity not in {"daily", "weekly", "monthly"}:
            raise ValueError("Periodicity must be one of: daily, weekly, monthly.")

        return cls(
            name=name,
            description=description,
            goal=goal,
            start_date=start_dt,
            periodicity=periodicity,
            reminder=reminder_time,
        )
