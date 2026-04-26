"""Watchlist: track keys that should alert when accessed or modified."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from envault.storage import get_vault_path


def _get_watchlist_path(vault_dir: Optional[str] = None) -> Path:
    base = Path(vault_dir) if vault_dir else get_vault_path()
    return base / "watchlist.json"


def _load_watchlist(vault_dir: Optional[str] = None) -> dict:
    path = _get_watchlist_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_watchlist(data: dict, vault_dir: Optional[str] = None) -> None:
    path = _get_watchlist_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def watch_key(key: str, reason: str = "", vault_dir: Optional[str] = None) -> None:
    """Add a key to the watchlist with an optional reason."""
    data = _load_watchlist(vault_dir)
    data[key] = {"reason": reason}
    _save_watchlist(data, vault_dir)


def unwatch_key(key: str, vault_dir: Optional[str] = None) -> bool:
    """Remove a key from the watchlist. Returns True if it was present."""
    data = _load_watchlist(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_watchlist(data, vault_dir)
    return True


def is_watched(key: str, vault_dir: Optional[str] = None) -> bool:
    """Return True if the key is on the watchlist."""
    data = _load_watchlist(vault_dir)
    return key in data


def get_watch_reason(key: str, vault_dir: Optional[str] = None) -> Optional[str]:
    """Return the reason a key is watched, or None if not watched."""
    data = _load_watchlist(vault_dir)
    entry = data.get(key)
    return entry["reason"] if entry is not None else None


def list_watched(vault_dir: Optional[str] = None) -> List[dict]:
    """Return a list of watched keys with their reasons."""
    data = _load_watchlist(vault_dir)
    return [{"key": k, "reason": v["reason"]} for k, v in sorted(data.items())]


def clear_watchlist(vault_dir: Optional[str] = None) -> int:
    """Remove all entries from the watchlist. Returns count removed."""
    data = _load_watchlist(vault_dir)
    count = len(data)
    _save_watchlist({}, vault_dir)
    return count
