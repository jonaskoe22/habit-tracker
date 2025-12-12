# app/cli.py
"""
Command-line interface for the Habit Tracker.

Responsibilities:
- Collect user input via an interactive menu
- Delegate logic to models (Habit) and persistence (Database)
- Call pure analytics functions from app.analysis.analyse
- Record completion history (date and time) for each check-off
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List

from app.db.database import Database
from app.models.habit import Habit
from app.models.user import User
from app.analysis.analyse import (
    list_all_habits,
    list_by_periodicity,
    longest_run_streak,
    longest_run_streak_for,
    print_summary,
)



# Small helpers

def _input(prompt: str) -> str:
    """Read input from the user and strip surrounding whitespace."""
    return input(prompt).strip()


def _rehydrate_habit_from_row(habit_row: Dict) -> Habit:
    """
    Recreate a Habit object from a database row.

    This allows us to reuse the streak logic implemented in the Habit model
    when checking off habits loaded from the database.
    """
    habit = Habit.from_form(
        habit_row["name"],
        habit_row["description"],
        habit_row["goal"],
        habit_row["start_date"],
        habit_row.get("periodicity", "daily"),
        habit_row["reminder"] if habit_row.get("reminder") else None,
    )

    habit.streak = int(habit_row.get("streak", 0))
    habit.completed = bool(habit_row.get("completed", 0))

    last = habit_row.get("last_completed_date")
    habit.last_completed_date = datetime.fromisoformat(last).date() if last else None

    return habit



# Demo data

def seed_demo_habits(db: Database, user: User) -> None:
    """
    Insert five predefined demo habits for a new user.

    The habits are only inserted if the user has no habits yet,
    so this function is safe to call on every startup.
    """
    if db.fetch_habits_by_user(user.user_id):
        return

    demo: List[Dict] = [
        dict(
            name="Drink Water",
            description="8 glasses",
            goal="Hydration",
            start_date="2025-01-01",
            periodicity="daily",
            reminder="09:00",
        ),
        dict(
            name="Read",
            description="Read 10 pages",
            goal="Learning",
            start_date="2025-01-01",
            periodicity="daily",
            reminder="20:30",
        ),
        dict(
            name="Meditate",
            description="5 minutes breathing",
            goal="Mindfulness",
            start_date="2025-01-01",
            periodicity="daily",
            reminder=None,
        ),
        dict(
            name="Call Family",
            description="Phone call to parents",
            goal="Relationships",
            start_date="2025-01-01",
            periodicity="weekly",
            reminder=None,
        ),
        dict(
            name="Budget Review",
            description="Review spending",
            goal="Finance",
            start_date="2025-01-01",
            periodicity="weekly",
            reminder="18:00",
        ),
    ]

    for h in demo:
        habit = Habit.from_form(
            h["name"],
            h["description"],
            h["goal"],
            h["start_date"],
            h["periodicity"],
            h["reminder"],
        )

        db.save_habit(
            user_id=user.user_id,
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



# User and habit flows

def create_user(db: Database) -> User:
    """Prompt for user details and store the user in the database."""
    name = _input("Enter your name: ")
    email = _input("Enter your email: ")

    user = User(name, email)
    user.user_id = db.save_user(user.name, user.email)
    return user


def add_habit_flow(db: Database, user: User) -> None:
    """Collect habit details from the user and save them."""
    print("\nAdd a new habit:")
    name = _input("Habit name: ")
    description = _input("Description: ")
    goal = _input("Goal: ")
    start_date = _input("Start date (YYYY-MM-DD): ")
    periodicity = _input("Periodicity (daily/weekly/monthly) [daily]: ") or "daily"
    reminder = _input("Reminder time (HH:MM, optional): ") or None

    try:
        habit = Habit.from_form(name, description, goal, start_date, periodicity, reminder)
    except ValueError as exc:
        print(f"Error: {exc}")
        return

    habit_id = db.save_habit(
        user_id=user.user_id,
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

    print(f"Saved habit '{habit.name}' (id={habit_id}).")


def list_habits_flow(db: Database, user: User) -> None:
    """List all habits belonging to the current user."""
    rows = db.fetch_habits_by_user(user.user_id)
    views = list_all_habits(rows)

    if not views:
        print("No habits yet.")
        return

    print("\nYour habits:")
    for v in views:
        last = v.last_completed_date or "—"
        print(f"#{v.id} • {v.name} | {v.periodicity} | streak={v.streak} | last={last}")


def check_off_flow(db: Database, user: User) -> None:
    """
    Mark a habit as completed today.

    This updates the streak, persists the new state,
    and stores a timestamped completion entry.
    """
    rows = db.fetch_habits_by_user(user.user_id)
    if not rows:
        print("You have no habits to check off.")
        return

    print("\nWhich habit did you complete?")
    for idx, r in enumerate(rows, start=1):
        print(f"{idx}. {r['name']} ({r['periodicity']}, streak={r['streak']})")

    try:
        selected = int(_input("> ")) - 1
        row = rows[selected]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    habit = _rehydrate_habit_from_row(row)
    today = date.today()
    habit.check_off(on_date=today)

    db.update_habit_progress(
        row["id"],
        int(habit.completed),
        habit.streak,
        habit.last_completed_date.isoformat(),
    )

    now_iso = datetime.now().isoformat(timespec="seconds")
    db.save_completion(habit_id=row["id"], completed_at_iso=now_iso)

    print(f"Checked off '{habit.name}'. Current streak: {habit.streak}")
    print(f"Completion logged at {now_iso}")


def view_history_flow(db: Database, user: User) -> None:
    """Show recent completion timestamps for a selected habit."""
    rows = db.fetch_habits_by_user(user.user_id)
    if not rows:
        print("No habits yet.")
        return

    for idx, r in enumerate(rows, start=1):
        print(f"{idx}. {r['name']}")

    try:
        selected = int(_input("> ")) - 1
        row = rows[selected]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    history = db.fetch_completions(row["id"], limit=20)
    if not history:
        print("No completions logged yet.")
    else:
        print(f"Completion history for '{row['name']}':")
        for h in history:
            print(f"  - {h['completed_at']}")


def delete_habit_flow(db: Database, user: User) -> None:
    """Delete one of the user's habits along with its completion history."""
    rows = db.fetch_habits_by_user(user.user_id)
    if not rows:
        print("You have no habits to delete.")
        return

    for idx, r in enumerate(rows, start=1):
        print(f"{idx}. {r['name']} ({r['periodicity']}, streak={r['streak']})")

    try:
        selected = int(_input("Which habit do you want to delete? ")) - 1
        row = rows[selected]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    db.delete_habit(row["id"])
    print(f"Deleted habit '{row['name']}'.")


def analytics_summary_flow(db: Database, user: User) -> None:
    """Print a compact analytics summary for the user's habits."""
    rows = db.fetch_habits_by_user(user.user_id)
    print_summary(rows)


def list_by_periodicity_flow(db: Database, user: User) -> None:
    """List habits filtered by a chosen periodicity."""
    period = _input("Which periodicity? (daily/weekly/monthly): ").lower()
    if period not in {"daily", "weekly", "monthly"}:
        print("Invalid periodicity.")
        return

    rows = db.fetch_habits_by_user(user.user_id)
    views = list_by_periodicity(rows, period)

    if not views:
        print(f"No {period} habits found.")
        return

    print(f"\n{period.title()} habits:")
    for v in views:
        last = v.last_completed_date or "—"
        print(f"#{v.id} • {v.name} | streak={v.streak} | last={last}")



# Main entry point

def main() -> None:
    """Run the Habit Tracker CLI."""
    db = Database(path="habits.sqlite3")
    db.initialize()

    print("Welcome to the Habit Tracker!")
    user = create_user(db)
    seed_demo_habits(db, user)

    while True:
        print("\nChoose an option:")
        print("1. Add a new habit")
        print("2. View all habits")
        print("3. Check off a habit")
        print("4. Analytics summary")
        print("5. View completion history")
        print("6. List habits by periodicity")
        print("7. Longest streak overall")
        print("8. Longest streak for a given habit")
        print("9. Delete a habit")
        print("10. Exit")

        choice = _input("Enter your choice: ")

        if choice == "1":
            add_habit_flow(db, user)
        elif choice == "2":
            list_habits_flow(db, user)
        elif choice == "3":
            check_off_flow(db, user)
        elif choice == "4":
            analytics_summary_flow(db, user)
        elif choice == "5":
            view_history_flow(db, user)
        elif choice == "6":
            list_by_periodicity_flow(db, user)
        elif choice == "7":
            rows = db.fetch_habits_by_user(user.user_id)
            habit_id, streak = longest_run_streak(rows)
            if habit_id is None:
                print("No habits yet.")
            else:
                print(f"Longest streak: {streak} (habit #{habit_id})")
        elif choice == "8":
            try:
                habit_id = int(_input("Enter habit id: "))
            except ValueError:
                print("Please enter a number.")
                continue

            rows = db.fetch_habits_by_user(user.user_id)
            print(f"Longest streak for habit #{habit_id}: {longest_run_streak_for(rows, habit_id)}")
        elif choice == "9":
            delete_habit_flow(db, user)
        elif choice == "10":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
