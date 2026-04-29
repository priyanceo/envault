"""Changelog module: maintain a human-readable changelog of vault mutations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

_CHANGELOG_FILE = "changelog.json"


def get_changelog_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _CHANGELOG_FILE


def _load_changelog(vault_dir: str) -> List[dict]:
    path = get_changelog_path(vault_dir)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _save_changelog(vault_dir: str, entries: List[dict]) -> None:
    path = get_changelog_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2))


def record_change(
    vault_dir: str,
    action: str,
    key: str,
    actor: Optional[str] = None,
    note: Optional[str] = None,
) -> dict:
    """Append a change entry and return it."""
    if not action:
        raise ValueError("action must not be empty")
    if not key:
        raise ValueError("key must not be empty")

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "key": key,
    }
    if actor:
        entry["actor"] = actor
    if note:
        entry["note"] = note

    entries = _load_changelog(vault_dir)
    entries.append(entry)
    _save_changelog(vault_dir, entries)
    return entry


def get_changelog(
    vault_dir: str,
    key: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    """Return changelog entries, optionally filtered by key and/or capped."""
    entries = _load_changelog(vault_dir)
    if key is not None:
        entries = [e for e in entries if e.get("key") == key]
    if limit is not None:
        entries = entries[-limit:]
    return entries


def clear_changelog(vault_dir: str) -> int:
    """Delete all changelog entries; return count removed."""
    entries = _load_changelog(vault_dir)
    count = len(entries)
    _save_changelog(vault_dir, [])
    return count
