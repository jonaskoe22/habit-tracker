# app/models/reminder.py
"""
Simple reminder model using a background scheduler.

This module provides a way to print reminder messages to the console at regular intervals.
"""

import threading
import time

import schedule


class Reminder:
    """
    Sends periodic console reminders for a habit.

    The reminder runs in a background thread so that it does not
    block the main application loop.
    """

    def __init__(self, habit_id: int, message: str) -> None:
        """
        Create a new reminder for a specific habit.

        Args:
            habit_id: ID of the habit the reminder belongs to.
            message: Message to display when the reminder triggers.
        """
        self.habit_id = habit_id
        self.message = message

    def send_message(self) -> None:
        """
        Print the reminder message to the console.
        """
        print(f"Reminder for habit #{self.habit_id}: {self.message}")

    def start(self) -> None:
        """
        Start the reminder in a background thread.

        The reminder is scheduled to run every 24 hours and will
        continue running until the application exits.
        """

        def runner():
            # Schedule the reminder to run once every 24 hours
            schedule.every(24).hours.do(self.send_message)

            # Keep checking for scheduled tasks
            while True:
                schedule.run_pending()
                time.sleep(1)

        # Run the scheduler in a daemon thread so it stops with the app
        threading.Thread(target=runner, daemon=True).start()
