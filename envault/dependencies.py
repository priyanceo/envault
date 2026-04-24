"""Dependency tracking between secrets.

Allows users to declare that one secret depends on another,
enabling warnings when a depended-upon secret is modified or deleted.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from envault.storage import get_vault_path


def _get_deps_path(vault_dir: str | None = None) -> Path:
    return get_vault_path(vault_dir) / "dependencies.json"


def _load_deps(vault_dir: str | None = None) -> Dict[str, List[str]]:
    """Return mapping of key -> list of keys that depend on it."""
    path = _get_deps_path(vault_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_deps(deps: Dict[str, List[str]], vault_dir: str | None = None) -> None:
    path = _get_deps_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(deps, indent=2))


def add_dependency(dependent: str, depends_on: str, vault_dir: str | None = None) -> None:
    """Record that *dependent* relies on *depends_on*."""
    if dependent == depends_on:
        raise ValueError("A secret cannot depend on itself.")
    deps = _load_deps(vault_dir)
    dependents = deps.setdefault(depends_on, [])
    if dependent not in dependents:
        dependents.append(dependent)
    _save_deps(deps, vault_dir)


def remove_dependency(dependent: str, depends_on: str, vault_dir: str | None = None) -> bool:
    """Remove the dependency link. Returns True if it existed."""
    deps = _load_deps(vault_dir)
    dependents = deps.get(depends_on, [])
    if dependent not in dependents:
        return False
    dependents.remove(dependent)
    if not dependents:
        del deps[depends_on]
    _save_deps(deps, vault_dir)
    return True


def get_dependents(key: str, vault_dir: str | None = None) -> List[str]:
    """Return list of secrets that depend on *key*."""
    return _load_deps(vault_dir).get(key, [])


def get_dependencies(key: str, vault_dir: str | None = None) -> List[str]:
    """Return list of secrets that *key* depends on."""
    deps = _load_deps(vault_dir)
    return [parent for parent, children in deps.items() if key in children]


def remove_all_for_key(key: str, vault_dir: str | None = None) -> None:
    """Remove all dependency records involving *key* (as either role)."""
    deps = _load_deps(vault_dir)
    # Remove as a dependency target
    deps.pop(key, None)
    # Remove as a dependent
    for parent in list(deps.keys()):
        if key in deps[parent]:
            deps[parent].remove(key)
        if not deps[parent]:
            del deps[parent]
    _save_deps(deps, vault_dir)
