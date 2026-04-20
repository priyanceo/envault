"""Tag management for vault secrets — assign, list, and filter secrets by tag."""

from __future__ import annotations

from typing import Dict, List, Optional

from envault.storage import load_vault, save_vault

_TAGS_KEY = "__tags__"


def get_tags_map(vault_dir: str, password: str) -> Dict[str, List[str]]:
    """Return the full tag map: {secret_key: [tag, ...]}."""
    vault = load_vault(vault_dir, password)
    return vault.get(_TAGS_KEY, {})


def set_tags(vault_dir: str, password: str, secret_key: str, tags: List[str]) -> None:
    """Replace the tag list for *secret_key*."""
    vault = load_vault(vault_dir, password)
    tag_map: Dict[str, List[str]] = vault.get(_TAGS_KEY, {})
    tag_map[secret_key] = sorted(set(tags))
    vault[_TAGS_KEY] = tag_map
    save_vault(vault_dir, password, vault)


def add_tag(vault_dir: str, password: str, secret_key: str, tag: str) -> None:
    """Add a single tag to *secret_key* (no-op if already present)."""
    vault = load_vault(vault_dir, password)
    tag_map: Dict[str, List[str]] = vault.get(_TAGS_KEY, {})
    current = set(tag_map.get(secret_key, []))
    current.add(tag)
    tag_map[secret_key] = sorted(current)
    vault[_TAGS_KEY] = tag_map
    save_vault(vault_dir, password, vault)


def remove_tag(vault_dir: str, password: str, secret_key: str, tag: str) -> None:
    """Remove a single tag from *secret_key* (no-op if absent)."""
    vault = load_vault(vault_dir, password)
    tag_map: Dict[str, List[str]] = vault.get(_TAGS_KEY, {})
    current = set(tag_map.get(secret_key, []))
    current.discard(tag)
    tag_map[secret_key] = sorted(current)
    vault[_TAGS_KEY] = tag_map
    save_vault(vault_dir, password, vault)


def list_by_tag(vault_dir: str, password: str, tag: str) -> List[str]:
    """Return all secret keys that carry *tag*."""
    tag_map = get_tags_map(vault_dir, password)
    return sorted(k for k, tags in tag_map.items() if tag in tags)


def get_tags(vault_dir: str, password: str, secret_key: str) -> List[str]:
    """Return the tags for a single *secret_key*."""
    tag_map = get_tags_map(vault_dir, password)
    return tag_map.get(secret_key, [])
