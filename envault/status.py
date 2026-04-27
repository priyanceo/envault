"""Key status aggregation: combines TTL, expiry, permissions, reminders, and lock info."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from envault.ttl import get_ttl, is_expired
from envault.access import get_permissions
from envault.remind import get_reminder, is_reminder_due
from envault.lock import is_unlocked


@dataclass
class KeyStatus:
    key: str
    exists: bool
    expired: bool = False
    ttl_expires_at: Optional[str] = None
    permissions: list[str] = field(default_factory=list)
    reminder_due: bool = False
    reminder_message: Optional[str] = None
    vault_unlocked: bool = False


def get_key_status(vault_dir: str, password: str, key: str) -> KeyStatus:
    """Return a consolidated status object for a given key."""
    from envault.storage import get_secret

    try:
        get_secret(vault_dir, password, key)
        exists = True
    except (KeyError, Exception):
        exists = False

    expired = is_expired(vault_dir, key) if exists else False
    ttl_info = get_ttl(vault_dir, key) if exists else None
    ttl_str = ttl_info.isoformat() if ttl_info else None

    perms = get_permissions(vault_dir, key) if exists else []

    reminder = get_reminder(vault_dir, key) if exists else None
    reminder_due = is_reminder_due(vault_dir, key) if (exists and reminder) else False
    reminder_msg = reminder.get("message") if reminder else None

    unlocked = is_unlocked(vault_dir, password)

    return KeyStatus(
        key=key,
        exists=exists,
        expired=expired,
        ttl_expires_at=ttl_str,
        permissions=perms,
        reminder_due=reminder_due,
        reminder_message=reminder_msg,
        vault_unlocked=unlocked,
    )


def format_status(status: KeyStatus) -> str:
    """Render a KeyStatus as a human-readable string."""
    lines = [f"Key      : {status.key}"]
    lines.append(f"Exists   : {'yes' if status.exists else 'no'}")
    if status.exists:
        lines.append(f"Expired  : {'yes' if status.expired else 'no'}")
        lines.append(f"TTL exp  : {status.ttl_expires_at or 'none'}")
        lines.append(f"Perms    : {', '.join(status.permissions) if status.permissions else 'all'}")
        lines.append(f"Reminder : {'DUE' if status.reminder_due else ('set' if status.reminder_message else 'none')}")
        if status.reminder_message:
            lines.append(f"  msg    : {status.reminder_message}")
    lines.append(f"Unlocked : {'yes' if status.vault_unlocked else 'no'}")
    return "\n".join(lines)
