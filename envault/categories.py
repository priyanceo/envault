"""Category management for vault secrets."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from envault.storage import get_vault_path, load_vault


def _get_categories_path(vault_dir: Optional[Path] = None) -> Path:
    base = vault_dir or get_vault_path()
    return base / "categories.json"


def _load_categories(vault_dir: Optional[Path] = None) -> Dict[str, List[str]]:
    path = _get_categories_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_categories(data: Dict[str, List[str]], vault_dir: Optional[Path] = None) -> None:
    path = _get_categories_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_category(key: str, category: str, password: str, vault_dir: Optional[Path] = None) -> None:
    """Assign a category to a secret key."""
    vault = load_vault(password, vault_dir=vault_dir)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault.")
    data = _load_categories(vault_dir)
    data[key] = category
    _save_categories(data, vault_dir)


def get_category(key: str, vault_dir: Optional[Path] = None) -> Optional[str]:
    """Return the category assigned to a key, or None."""
    data = _load_categories(vault_dir)
    return data.get(key)


def remove_category(key: str, vault_dir: Optional[Path] = None) -> bool:
    """Remove the category for a key. Returns True if removed, False if not set."""
    data = _load_categories(vault_dir)
    if key not in data:
        return False
    del data[key]
    _save_categories(data, vault_dir)
    return True


def list_by_category(category: str, vault_dir: Optional[Path] = None) -> List[str]:
    """Return all keys assigned to the given category, sorted."""
    data = _load_categories(vault_dir)
    return sorted(k for k, v in data.items() if v == category)


def list_all_categories(vault_dir: Optional[Path] = None) -> Dict[str, str]:
    """Return a mapping of key -> category for all categorised keys."""
    return dict(_load_categories(vault_dir))


def get_unique_categories(vault_dir: Optional[Path] = None) -> List[str]:
    """Return a sorted list of all distinct category names in use."""
    data = _load_categories(vault_dir)
    unique: Set[str] = set(data.values())
    return sorted(unique)
