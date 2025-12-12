"""
SQLite-backed persistence layer for users, habits, and completion history.

This module is responsible for all database access and hides raw SQL
from the rest of the application.
"""

import sqlite3
from typing import Any, Dict, List, Optional


class Database:
    """
    Small wrapper around sqlite3.

    The Database class handles table creation and provides
    methods to store and retrieve users, habits, and completion events.

    Args:
        path: Path to the SQLite database file.
              Use ':memory:' for temporary in-memory databases in tests.
    """

    def __init__(self, path: str = ":memory:") -> None:
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    
    # Schema setup
    
    def initialize(self) -> None:
        """
        Create database tables if they do not already exist.

        This method must be called once before any other database
        operations are performed.
        """
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()

        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                goal TEXT NOT NULL,
                start_date TEXT NOT NULL,
                periodicity TEXT NOT NULL DEFAULT 'daily',
                reminder TEXT,
                completed INTEGER NOT NULL DEFAULT 0,
                streak INTEGER NOT NULL DEFAULT 0,
                last_completed_date TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            -- Store every completion event with date and time
            CREATE TABLE IF NOT EXISTS habit_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY(habit_id) REFERENCES habits(id)
            );
            """
        )
        self.conn.commit()

    # ------------------------------------------------------------------ #
    # Users
    # ------------------------------------------------------------------ #
    def save_user(self, name: str, email: str) -> int:
        """
        Insert a new user into the database.

        Returns:
            The newly created user ID.
        """
        cur = self.conn.cursor()
        cur.execute("INSERT INTO users(name, email) VALUES (?, ?)", (name, email))
        self.conn.commit()
        return int(cur.lastrowid)

    
    # Habits
    
    def save_habit(self, **fields: Any) -> int:
        """
        Insert a habit row using keyword arguments.

        Returns:
            The newly created habit ID.
        """
        keys = ",".join(fields.keys())
        placeholders = ",".join(["?"] * len(fields))
        values = tuple(fields.values())

        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO habits({keys}) VALUES ({placeholders})", values)
        self.conn.commit()
