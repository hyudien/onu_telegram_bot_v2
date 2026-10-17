"""Allowed user storage"""

import json
import os

from app.config import ADMIN_ID

USERS_FILE = os.path.join(os.path.dirname(__file__), "allowed_users.json")


def load_users() -> list:
    """Return the list of allowed user IDs (admin is always allowed)."""
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = [int(u) for u in json.load(f)]
        except (ValueError, TypeError, OSError):
            users = []
    if ADMIN_ID not in users:
        users.append(ADMIN_ID)
    return users


def save_users(users: list) -> None:
    tmp = USERS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
    os.replace(tmp, USERS_FILE)


def add_user(user_id: int) -> None:
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)


def is_allowed(user_id: int) -> bool:
    return user_id in load_users()
