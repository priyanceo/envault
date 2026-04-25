"""Favorites module — mark secrets as favorites for quick access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envault.storage import get_vault_path, get_secret


def _get_favorites_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "favorites.json"


def _load_favorites(vault_dir: str) -> List[str]:
    path = _get_favorites_path(vault_dir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def _save_favorites(vault_dir: str, favorites: List[str]) -> None:
    path = _get_favorites_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(favorites)), indent=2))


def add_favorite(vault_dir: str, password: str, key: str) -> None:
    """Mark *key* as a favorite. Raises KeyError if the key does not exist."""
    # Validate the key exists in the vault
    value = get_secret(vault_dir, password, key)
    if value is None:
        raise KeyError(f"Secret '{key}' not found in vault.")
    favorites = _load_favorites(vault_dir)
    if key not in favorites:
        favorites.append(key)
        _save_favorites(vault_dir, favorites)


def remove_favorite(vault_dir: str, key: str) -> bool:
    """Remove *key* from favorites. Returns True if it was present."""
    favorites = _load_favorites(vault_dir)
    if key in favorites:
        favorites.remove(key)
        _save_favorites(vault_dir, favorites)
        return True
    return False


def list_favorites(vault_dir: str) -> List[str]:
    """Return a sorted list of favorite keys."""
    return sorted(_load_favorites(vault_dir))


def is_favorite(vault_dir: str, key: str) -> bool:
    """Return True if *key* is marked as a favorite."""
    return key in _load_favorites(vault_dir)
