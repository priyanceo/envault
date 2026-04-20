"""TTL (time-to-live) support for vault secrets."""

from __future__ import annotations

import time
from typing import Optional

from envault.storage import load_vault, save_vault

TTL_NAMESPACE = "__ttl__"


def set_ttl(vault_dir: str, password: str, key: str, seconds: int) -> None:
    """Attach a TTL (expiry timestamp) to an existing secret."""
    vault = load_vault(vault_dir, password)
    if key not in vault:
        raise KeyError(f"Key '{key}' not found in vault.")
    ttl_map = vault.get(TTL_NAMESPACE, {})
    ttl_map[key] = time.time() + seconds
    vault[TTL_NAMESPACE] = ttl_map
    save_vault(vault_dir, password, vault)


def get_ttl(vault_dir: str, password: str, key: str) -> Optional[float]:
    """Return the expiry timestamp for *key*, or None if no TTL is set."""
    vault = load_vault(vault_dir, password)
    return vault.get(TTL_NAMESPACE, {}).get(key)


def remove_ttl(vault_dir: str, password: str, key: str) -> None:
    """Remove the TTL for *key* without deleting the secret itself."""
    vault = load_vault(vault_dir, password)
    ttl_map = vault.get(TTL_NAMESPACE, {})
    ttl_map.pop(key, None)
    vault[TTL_NAMESPACE] = ttl_map
    save_vault(vault_dir, password, vault)


def is_expired(vault_dir: str, password: str, key: str) -> bool:
    """Return True if the secret's TTL has elapsed."""
    expiry = get_ttl(vault_dir, password, key)
    if expiry is None:
        return False
    return time.time() >= expiry


def purge_expired(vault_dir: str, password: str) -> list[str]:
    """Delete all secrets whose TTL has elapsed. Returns list of purged keys."""
    vault = load_vault(vault_dir, password)
    ttl_map = vault.get(TTL_NAMESPACE, {})
    now = time.time()
    purged: list[str] = []
    for key, expiry in list(ttl_map.items()):
        if now >= expiry:
            vault.pop(key, None)
            ttl_map.pop(key)
            purged.append(key)
    vault[TTL_NAMESPACE] = ttl_map
    save_vault(vault_dir, password, vault)
    return purged
