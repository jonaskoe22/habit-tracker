# app/analysis/analyse.py
"""Analytics for habits implemented.

This module contains pure functions that operate on row-like dictionaries. 
Functions do not mutate input data and do not access the database directly.

Required functionality:
- return a list of all currently tracked habits,
- return a list of all habits with the same periodicity,
- return the longest run streak across all habits,
- return the longest run streak for a given habit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Tuple, Optional, Literal, Any

Periodicity = Literal["daily", "weekly", "monthly"]
Row = Mapping[str, Any]



# Immutable habit view

@dataclass(frozen=True)
class HabitView:
    """Immutable view of a habit row.

    Attributes:
        id: Unique identifier of the habit.
        name: Habit name.
        periodicity: "daily", "weekly", or "monthly".
        streak: Current streak count.
        last_completed_date: Last completion date (YYYY-MM-DD) or None.
    """

    id: int
    name: str
    periodicity: Periodicity
    streak: int
    last_completed_date: Optional[str]


def _as_view(row: Row) -> HabitView:
    """Convert a DB row mapping into an immutable HabitView."""
    return HabitView(
        id=int(row["id"]),
        name=str(row["name"]),
        periodicity=row.get("periodicity", "daily"),
        streak=int(row.get("streak", 0)),
        last_completed_date=row.get("last_completed_date"),
    )



# Pure analytics functions

def list_all_habits(rows: Iterable[Row]) -> List[HabitView]:
    """Return all currently tracked habits as HabitView objects."""
    return list(map(_as_view, rows))


def list_by_periodicity(rows: Iterable[Row], periodicity: Periodicity) -> List[HabitView]:
    """Return all habits that match the given periodicity."""
    return list(map(_as_view, filter(lambda r: r.get("periodicity") == periodicity, rows)))


def longest_run_streak(rows: Iterable[Row]) -> Tuple[Optional[int], int]:
    """Return (habit_id, longest_streak) across all habits.

    If there are no habits, returns (None, 0).
    """
    views = list_all_habits(rows)
    if not views:
        return (None, 0)

    top = max(views, key=lambda v: v.streak)
    return (top.id, top.streak)


def longest_run_streak_for(rows: Iterable[Row], habit_id: int) -> int:
    """Return the streak value for a given habit_id.

    Returns 0 if the habit_id is not present in rows.
    """
    match = next((r for r in rows if int(r["id"]) == habit_id), None)
    return int(match.get("streak", 0)) if match else 0



# Convenience: print summary

def print_summary(rows: Iterable[Row]) -> None:
    """Print a compact summary (uses only the pure analytics functions)."""
    views = list_all_habits(rows)
    if not views:
        print("No habits to analyse.")
        return

    print("== Habit Summary ==")
    for v in views:
        last = v.last_completed_date or "—"
        print(f"#{v.id} • {v.name} | {v.periodicity} | streak={v.streak} | last={last}")

    habit_id, mx = longest_run_streak(rows)
    if habit_id is None:
        print("Longest streak: 0")
    else:
        print(f"Longest streak overall: {mx} (habit #{habit_id})")
