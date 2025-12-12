# app/models/user.py
"""
User model for the habit tracker.

"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """
    Represents a user of the habit tracker.

    The user ID is assigned by the database when the user is first saved.
    """

    name: str
    email: str
    user_id: Optional[int] = None
