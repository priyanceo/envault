"""Pre/post hooks for vault operations (set, get, delete)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

VALID_EVENTS = ("pre-set", "post-set", "pre-get", "post-get", "pre-delete", "post-delete")


def get_hooks_path(vault_dir: Optional[str] = None) -> Path:
    base = Path(vault_dir) if vault_dir else Path.home() / ".envault"
    return base / "hooks.json"


def _load_hooks(vault_dir: Optional[str] = None) -> Dict[str, List[str]]:
    path = get_hooks_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_hooks(hooks: Dict[str, List[str]], vault_dir: Optional[str] = None) -> None:
    path = get_hooks_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(hooks, f, indent=2)


def register_hook(event: str, command: str, vault_dir: Optional[str] = None) -> None:
    """Register a shell command to run on a given event."""
    if event not in VALID_EVENTS:
        raise ValueError(f"Invalid event '{event}'. Valid events: {VALID_EVENTS}")
    hooks = _load_hooks(vault_dir)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    _save_hooks(hooks, vault_dir)


def unregister_hook(event: str, command: str, vault_dir: Optional[str] = None) -> bool:
    """Remove a registered hook. Returns True if removed, False if not found."""
    hooks = _load_hooks(vault_dir)
    if event in hooks and command in hooks[event]:
        hooks[event].remove(command)
        if not hooks[event]:
            del hooks[event]
        _save_hooks(hooks, vault_dir)
        return True
    return False


def get_hooks(event: str, vault_dir: Optional[str] = None) -> List[str]:
    """Return all commands registered for an event."""
    hooks = _load_hooks(vault_dir)
    return hooks.get(event, [])


def list_hooks(vault_dir: Optional[str] = None) -> Dict[str, List[str]]:
    """Return all hooks grouped by event."""
    return _load_hooks(vault_dir)


def fire_hooks(event: str, vault_dir: Optional[str] = None) -> List[int]:
    """Execute all commands registered for an event. Returns list of exit codes."""
    results = []
    for cmd in get_hooks(event, vault_dir):
        code = os.system(cmd)  # noqa: S605
        results.append(code)
    return results
