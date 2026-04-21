"""Secret value history tracking for envault."""

import json
import time
from pathlib import Path
from typing import List, Optional

from envault.storage import get_vault_path


def get_history_path(vault_dir: Optional[Path] = None) -> Path:
    base = get_vault_path(vault_dir).parent
    return base / "history.json"


def _load_history(vault_dir: Optional[Path] = None) -> dict:
    path = get_history_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_history(data: dict, vault_dir: Optional[Path] = None) -> None:
    path = get_history_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def record_change(key: str, value: str, vault_dir: Optional[Path] = None) -> None:
    """Append a new history entry for the given key."""
    data = _load_history(vault_dir)
    if key not in data:
        data[key] = []
    data[key].append({"value": value, "timestamp": time.time()})
    _save_history(data, vault_dir)


def get_history(key: str, vault_dir: Optional[Path] = None) -> List[dict]:
    """Return the list of historical entries for a key, oldest first."""
    data = _load_history(vault_dir)
    return data.get(key, [])


def clear_history(key: str, vault_dir: Optional[Path] = None) -> bool:
    """Remove all history for a key. Returns True if key existed."""
    data = _load_history(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_history(data, vault_dir)
    return True


def list_keys_with_history(vault_dir: Optional[Path] = None) -> List[str]:
    """Return all keys that have at least one history entry."""
    data = _load_history(vault_dir)
    return [k for k, v in data.items() if v]
