"""Mentions module: track which secrets reference other secrets by key name."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

from envault.storage import get_vault_path

_MENTION_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}|\$([A-Z_][A-Z0-9_]*)")


def _get_mentions_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "mentions.json"


def _load_mentions(vault_dir: str) -> Dict[str, List[str]]:
    path = _get_mentions_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_mentions(vault_dir: str, data: Dict[str, List[str]]) -> None:
    path = _get_mentions_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def extract_mentions(value: str) -> List[str]:
    """Return all key names referenced inside *value* via ${KEY} or $KEY syntax."""
    found = []
    for m in _MENTION_RE.finditer(value):
        key = m.group(1) or m.group(2)
        if key and key not in found:
            found.append(key)
    return found


def update_mentions(vault_dir: str, source_key: str, value: str) -> List[str]:
    """Recompute mentions for *source_key* based on its current *value*."""
    data = _load_mentions(vault_dir)
    refs = extract_mentions(value)
    if refs:
        data[source_key] = refs
    else:
        data.pop(source_key, None)
    _save_mentions(vault_dir, data)
    return refs


def get_mentions(vault_dir: str, source_key: str) -> List[str]:
    """Return keys that *source_key* references."""
    return _load_mentions(vault_dir).get(source_key, [])


def get_reverse_mentions(vault_dir: str, target_key: str) -> List[str]:
    """Return keys that reference *target_key*."""
    data = _load_mentions(vault_dir)
    return [src for src, refs in data.items() if target_key in refs]


def remove_mentions(vault_dir: str, source_key: str) -> bool:
    """Remove all mention records originating from *source_key*."""
    data = _load_mentions(vault_dir)
    if source_key in data:
        del data[source_key]
        _save_mentions(vault_dir, data)
        return True
    return False


def list_all_mentions(vault_dir: str) -> Dict[str, List[str]]:
    """Return the full mentions map."""
    return dict(_load_mentions(vault_dir))
