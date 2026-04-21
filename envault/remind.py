"""Reminders: schedule expiry reminders for secrets based on age or custom dates."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path


def get_reminders_path(vault_dir: Optional[str] = None) -> Path:
    return Path(get_vault_path(vault_dir)).parent / "reminders.json"


def _load_reminders(vault_dir: Optional[str] = None) -> dict:
    path = get_reminders_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_reminders(data: dict, vault_dir: Optional[str] = None) -> None:
    path = get_reminders_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def set_reminder(key: str, remind_at: datetime, vault_dir: Optional[str] = None) -> None:
    """Set a reminder for a secret key at a specific UTC datetime."""
    data = _load_reminders(vault_dir)
    data[key] = remind_at.astimezone(timezone.utc).isoformat()
    _save_reminders(data, vault_dir)


def get_reminder(key: str, vault_dir: Optional[str] = None) -> Optional[datetime]:
    """Return the reminder datetime for a key, or None if not set."""
    data = _load_reminders(vault_dir)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def remove_reminder(key: str, vault_dir: Optional[str] = None) -> bool:
    """Remove a reminder for a key. Returns True if it existed."""
    data = _load_reminders(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_reminders(data, vault_dir)
    return True


def get_due_reminders(vault_dir: Optional[str] = None) -> list[tuple[str, datetime]]:
    """Return all (key, remind_at) pairs whose remind_at is in the past."""
    data = _load_reminders(vault_dir)
    now = datetime.now(timezone.utc)
    due = []
    for key, raw in data.items():
        remind_at = datetime.fromisoformat(raw)
        if remind_at <= now:
            due.append((key, remind_at))
    due.sort(key=lambda x: x[1])
    return due


def list_reminders(vault_dir: Optional[str] = None) -> list[tuple[str, datetime]]:
    """Return all reminders sorted by datetime."""
    data = _load_reminders(vault_dir)
    items = [(k, datetime.fromisoformat(v)) for k, v in data.items()]
    items.sort(key=lambda x: x[1])
    return items
