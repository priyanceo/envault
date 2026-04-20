"""Access control: per-key read/write permissions stored in the vault."""

from __future__ import annotations

from typing import Optional

from envault.storage import load_vault, save_vault

ACCESS_META_KEY = "__access_control__"

ALL_PERMS = {"read", "write"}


def _get_acl(vault: dict) -> dict:
    meta = vault.get("meta", {})
    return meta.get(ACCESS_META_KEY, {})


def _set_acl(vault: dict, acl: dict) -> dict:
    vault.setdefault("meta", {})[ACCESS_META_KEY] = acl
    return vault


def set_permissions(key: str, permissions: set[str], password: str, vault_dir: Optional[str] = None) -> None:
    """Set allowed permissions for a key. Permissions is a subset of {'read', 'write'}."""
    unknown = permissions - ALL_PERMS
    if unknown:
        raise ValueError(f"Unknown permissions: {unknown}. Allowed: {ALL_PERMS}")
    vault = load_vault(password, vault_dir=vault_dir)
    if key not in vault.get("secrets", {}):
        raise KeyError(f"Key '{key}' not found in vault.")
    acl = _get_acl(vault)
    acl[key] = sorted(permissions)
    _set_acl(vault, acl)
    save_vault(vault, password, vault_dir=vault_dir)


def get_permissions(key: str, password: str, vault_dir: Optional[str] = None) -> set[str]:
    """Return the set of permissions for a key. Defaults to all permissions if unset."""
    vault = load_vault(password, vault_dir=vault_dir)
    acl = _get_acl(vault)
    if key not in acl:
        return set(ALL_PERMS)
    return set(acl[key])


def remove_permissions(key: str, password: str, vault_dir: Optional[str] = None) -> None:
    """Remove explicit ACL entry for a key (reverts to default: all perms)."""
    vault = load_vault(password, vault_dir=vault_dir)
    acl = _get_acl(vault)
    acl.pop(key, None)
    _set_acl(vault, acl)
    save_vault(vault, password, vault_dir=vault_dir)


def check_permission(key: str, permission: str, password: str, vault_dir: Optional[str] = None) -> bool:
    """Return True if the given permission is granted for the key."""
    return permission in get_permissions(key, password, vault_dir=vault_dir)


def list_acl(password: str, vault_dir: Optional[str] = None) -> dict[str, list[str]]:
    """Return the full ACL map: {key: [permissions]}."""
    vault = load_vault(password, vault_dir=vault_dir)
    return dict(_get_acl(vault))
