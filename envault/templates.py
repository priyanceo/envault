"""Template management for envault: save and apply key skeletons."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def get_templates_path(vault_dir: Path) -> Path:
    return vault_dir / "templates.json"


def _load_templates(vault_dir: Path) -> Dict[str, List[str]]:
    path = get_templates_path(vault_dir)
    if not path.exists():
        return {}
    with path.open("r") as f:
        return json.load(f)


def _save_templates(vault_dir: Path, data: Dict[str, List[str]]) -> None:
    path = get_templates_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def save_template(vault_dir: Path, name: str, keys: List[str]) -> None:
    """Save a named template containing a list of expected keys."""
    if not keys:
        raise ValueError("Template must contain at least one key.")
    data = _load_templates(vault_dir)
    data[name] = sorted(set(keys))
    _save_templates(vault_dir, data)


def get_template(vault_dir: Path, name: str) -> Optional[List[str]]:
    """Return the key list for a named template, or None if not found."""
    return _load_templates(vault_dir).get(name)


def list_templates(vault_dir: Path) -> List[str]:
    """Return all template names."""
    return sorted(_load_templates(vault_dir).keys())


def delete_template(vault_dir: Path, name: str) -> bool:
    """Delete a template by name. Returns True if it existed."""
    data = _load_templates(vault_dir)
    if name not in data:
        return False
    del data[name]
    _save_templates(vault_dir, data)
    return True


def check_template(vault_dir: Path, name: str, present_keys: List[str]) -> Dict[str, List[str]]:
    """Compare present_keys against a template.

    Returns a dict with:
      'missing'  – keys in template but not in present_keys
      'extra'    – keys in present_keys but not in template
    """
    template_keys = get_template(vault_dir, name)
    if template_keys is None:
        raise KeyError(f"Template '{name}' not found.")
    template_set = set(template_keys)
    present_set = set(present_keys)
    return {
        "missing": sorted(template_set - present_set),
        "extra": sorted(present_set - template_set),
    }
