"""Priority management for vault secrets."""

from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path, get_secret

_VALID_PRIORITIES = {"low", "medium", "high", "critical"}
_PRIORITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def _get_priority_path(vault_dir: Path) -> Path:
    return vault_dir / "priorities.json"


def _load_priorities(vault_dir: Path) -> dict:
    import json
    p = _get_priority_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(vault_dir: Path, data: dict) -> None:
    import json
    p = _get_priority_path(vault_dir)
    p.write_text(json.dumps(data, indent=2))


def set_priority(vault_dir: Path, password: str, key: str, priority: str) -> None:
    """Set priority for a secret key. Priority must be one of: low, medium, high, critical."""
    if priority not in _VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Must be one of: {sorted(_VALID_PRIORITIES)}")
    # Ensure the key exists in the vault
    get_secret(vault_dir, password, key)
    data = _load_priorities(vault_dir)
    data[key] = priority
    _save_priorities(vault_dir, data)


def get_priority(vault_dir: Path, key: str) -> Optional[str]:
    """Get priority for a secret key. Returns None if not set."""
    data = _load_priorities(vault_dir)
    return data.get(key)


def remove_priority(vault_dir: Path, key: str) -> bool:
    """Remove priority for a secret key. Returns True if removed, False if not set."""
    data = _load_priorities(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_priorities(vault_dir, data)
    return True


def list_by_priority(vault_dir: Path, priority: str) -> list[str]:
    """List all keys with the given priority, sorted alphabetically."""
    if priority not in _VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Must be one of: {sorted(_VALID_PRIORITIES)}")
    data = _load_priorities(vault_dir)
    return sorted(k for k, v in data.items() if v == priority)


def get_all_priorities(vault_dir: Path) -> dict[str, str]:
    """Return all key->priority mappings sorted by priority level descending, then key."""
    data = _load_priorities(vault_dir)
    return dict(
        sorted(data.items(), key=lambda item: (-_PRIORITY_ORDER.get(item[1], 0), item[0]))
    )
