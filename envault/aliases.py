"""Alias management for envault secrets.

Allows users to create short aliases that map to full secret keys,
making it easier to reference frequently used secrets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path


def _get_aliases_path(vault_dir: Optional[Path] = None) -> Path:
    return get_vault_path(vault_dir).parent / "aliases.json"


def _load_aliases(vault_dir: Optional[Path] = None) -> dict[str, str]:
    path = _get_aliases_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_aliases(aliases: dict[str, str], vault_dir: Optional[Path] = None) -> None:
    path = _get_aliases_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(aliases, indent=2))


def set_alias(alias: str, key: str, vault_dir: Optional[Path] = None) -> None:
    """Map an alias name to a secret key."""
    if not alias or not alias.strip():
        raise ValueError("Alias name must not be empty.")
    if not key or not key.strip():
        raise ValueError("Target key must not be empty.")
    aliases = _load_aliases(vault_dir)
    aliases[alias] = key
    _save_aliases(aliases, vault_dir)


def get_alias(alias: str, vault_dir: Optional[Path] = None) -> Optional[str]:
    """Return the key mapped to an alias, or None if not found."""
    return _load_aliases(vault_dir).get(alias)


def remove_alias(alias: str, vault_dir: Optional[Path] = None) -> bool:
    """Remove an alias. Returns True if it existed, False otherwise."""
    aliases = _load_aliases(vault_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    _save_aliases(aliases, vault_dir)
    return True


def list_aliases(vault_dir: Optional[Path] = None) -> dict[str, str]:
    """Return all aliases as a dict mapping alias -> key."""
    return dict(_load_aliases(vault_dir))


def resolve(alias_or_key: str, vault_dir: Optional[Path] = None) -> str:
    """Resolve an alias to its key, or return the input unchanged if not an alias."""
    return _load_aliases(vault_dir).get(alias_or_key, alias_or_key)
