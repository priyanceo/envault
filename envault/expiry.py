"""Key expiry management: set, get, and check expiry dates for secrets."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path, get_secret

_EXPIRY_FILENAME = "expiry.json"


def _get_expiry_path(vault_dir: str) -> Path:
    return Path(vault_dir) / _EXPIRY_FILENAME


def _load_expiry(vault_dir: str) -> dict:
    path = _get_expiry_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_expiry(vault_dir: str, data: dict) -> None:
    path = _get_expiry_path(vault_dir)
    path.write_text(json.dumps(data, indent=2))


def set_expiry(vault_dir: str, password: str, key: str, expires_at: datetime) -> None:
    """Set an expiry datetime (UTC) for a key. Raises KeyError if key not found."""
    # Verify key exists
    get_secret(vault_dir, password, key)
    data = _load_expiry(vault_dir)
    data[key] = expires_at.astimezone(timezone.utc).isoformat()
    _save_expiry(vault_dir, data)


def get_expiry(vault_dir: str, key: str) -> Optional[datetime]:
    """Return the expiry datetime (UTC) for a key, or None if not set."""
    data = _load_expiry(vault_dir)
    raw = data.get(key)
    if raw is None:
        return None
    return datetime.fromisoformat(raw)


def remove_expiry(vault_dir: str, key: str) -> bool:
    """Remove the expiry for a key. Returns True if removed, False if not present."""
    data = _load_expiry(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_expiry(vault_dir, data)
    return True


def is_expired(vault_dir: str, key: str) -> bool:
    """Return True if the key has an expiry that is in the past."""
    expiry = get_expiry(vault_dir, key)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= expiry


def list_expiring(vault_dir: str) -> list[tuple[str, datetime]]:
    """Return all keys that have an expiry set, sorted by expiry date ascending."""
    data = _load_expiry(vault_dir)
    result = [(k, datetime.fromisoformat(v)) for k, v in data.items()]
    result.sort(key=lambda x: x[1])
    return result
