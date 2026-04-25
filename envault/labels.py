"""Label management for vault secrets — attach arbitrary key/value metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envault.storage import get_vault_path, get_secret


def _get_labels_path(vault_dir: Optional[str] = None) -> Path:
    base = Path(vault_dir) if vault_dir else get_vault_path().parent
    return base / "labels.json"


def _load_labels(vault_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    path = _get_labels_path(vault_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_labels(data: Dict[str, Dict[str, str]], vault_dir: Optional[str] = None) -> None:
    path = _get_labels_path(vault_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def set_label(key: str, label_key: str, label_value: str, password: str, vault_dir: Optional[str] = None) -> None:
    """Attach a label to a secret. Raises KeyError if the secret does not exist."""
    get_secret(key, password, vault_dir=vault_dir)  # validates key exists
    data = _load_labels(vault_dir)
    data.setdefault(key, {})[label_key] = label_value
    _save_labels(data, vault_dir)


def get_labels(key: str, vault_dir: Optional[str] = None) -> Dict[str, str]:
    """Return all labels for a secret key."""
    return _load_labels(vault_dir).get(key, {})


def remove_label(key: str, label_key: str, vault_dir: Optional[str] = None) -> bool:
    """Remove a single label from a secret. Returns True if it existed."""
    data = _load_labels(vault_dir)
    if key in data and label_key in data[key]:
        del data[key][label_key]
        if not data[key]:
            del data[key]
        _save_labels(data, vault_dir)
        return True
    return False


def clear_labels(key: str, vault_dir: Optional[str] = None) -> None:
    """Remove all labels for a secret key."""
    data = _load_labels(vault_dir)
    if key in data:
        del data[key]
        _save_labels(data, vault_dir)


def find_by_label(label_key: str, label_value: Optional[str] = None, vault_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """Return secrets whose labels match label_key (and optionally label_value)."""
    data = _load_labels(vault_dir)
    results = {}
    for secret_key, labels in data.items():
        if label_key in labels:
            if label_value is None or labels[label_key] == label_value:
                results[secret_key] = labels
    return results
