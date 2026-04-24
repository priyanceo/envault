"""Group management for envault — organize secrets into named groups."""

from __future__ import annotations

from typing import Dict, List

from envault.storage import load_vault, save_vault

_GROUPS_KEY = "__groups__"


def _get_groups_map(vault_dir: str, password: str) -> Dict[str, List[str]]:
    """Load the groups map from the vault."""
    data = load_vault(vault_dir, password)
    return data.get(_GROUPS_KEY, {})


def _set_groups_map(vault_dir: str, password: str, groups: Dict[str, List[str]]) -> None:
    """Persist the groups map into the vault."""
    data = load_vault(vault_dir, password)
    data[_GROUPS_KEY] = groups
    save_vault(vault_dir, password, data)


def list_groups(vault_dir: str, password: str) -> List[str]:
    """Return a sorted list of all group names."""
    return sorted(_get_groups_map(vault_dir, password).keys())


def create_group(vault_dir: str, password: str, group: str) -> None:
    """Create an empty group if it does not already exist."""
    groups = _get_groups_map(vault_dir, password)
    if group not in groups:
        groups[group] = []
        _set_groups_map(vault_dir, password, groups)


def delete_group(vault_dir: str, password: str, group: str) -> bool:
    """Delete a group. Returns True if it existed, False otherwise."""
    groups = _get_groups_map(vault_dir, password)
    if group not in groups:
        return False
    del groups[group]
    _set_groups_map(vault_dir, password, groups)
    return True


def add_key_to_group(vault_dir: str, password: str, group: str, key: str) -> None:
    """Add a secret key to a group, creating the group if necessary."""
    data = load_vault(vault_dir, password)
    if key not in data:
        raise KeyError(f"Secret '{key}' does not exist in the vault.")
    groups = _get_groups_map(vault_dir, password)
    groups.setdefault(group, [])
    if key not in groups[group]:
        groups[group].append(key)
    _set_groups_map(vault_dir, password, groups)


def remove_key_from_group(vault_dir: str, password: str, group: str, key: str) -> bool:
    """Remove a key from a group. Returns True if removed, False if not present."""
    groups = _get_groups_map(vault_dir, password)
    if group not in groups or key not in groups[group]:
        return False
    groups[group].remove(key)
    _set_groups_map(vault_dir, password, groups)
    return True


def get_group_keys(vault_dir: str, password: str, group: str) -> List[str]:
    """Return the list of secret keys belonging to a group."""
    groups = _get_groups_map(vault_dir, password)
    if group not in groups:
        raise KeyError(f"Group '{group}' does not exist.")
    return list(groups[group])
