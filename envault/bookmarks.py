"""Bookmarks: mark frequently accessed secrets for quick retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault.storage import get_vault_path, get_secret


def _get_bookmarks_path(vault_dir: str | None = None) -> Path:
    return Path(get_vault_path(vault_dir)).parent / "bookmarks.json"


def _load_bookmarks(vault_dir: str | None = None) -> List[str]:
    path = _get_bookmarks_path(vault_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_bookmarks(bookmarks: List[str], vault_dir: str | None = None) -> None:
    path = _get_bookmarks_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(bookmarks)), indent=2))


def add_bookmark(key: str, password: str, vault_dir: str | None = None) -> bool:
    """Add a key to bookmarks. Raises KeyError if the key does not exist."""
    # Validate the key exists in the vault
    get_secret(key, password, vault_dir=vault_dir)
    bookmarks = _load_bookmarks(vault_dir)
    if key in bookmarks:
        return False
    bookmarks.append(key)
    _save_bookmarks(bookmarks, vault_dir)
    return True


def remove_bookmark(key: str, vault_dir: str | None = None) -> bool:
    """Remove a key from bookmarks. Returns False if not bookmarked."""
    bookmarks = _load_bookmarks(vault_dir)
    if key not in bookmarks:
        return False
    bookmarks.remove(key)
    _save_bookmarks(bookmarks, vault_dir)
    return True


def list_bookmarks(vault_dir: str | None = None) -> List[str]:
    """Return sorted list of bookmarked keys."""
    return sorted(_load_bookmarks(vault_dir))


def is_bookmarked(key: str, vault_dir: str | None = None) -> bool:
    """Return True if the key is bookmarked."""
    return key in _load_bookmarks(vault_dir)


def clear_bookmarks(vault_dir: str | None = None) -> int:
    """Remove all bookmarks. Returns count of removed entries."""
    bookmarks = _load_bookmarks(vault_dir)
    count = len(bookmarks)
    _save_bookmarks([], vault_dir)
    return count
