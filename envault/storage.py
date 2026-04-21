"""Persistent encrypted vault storage for envault."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from envault.crypto import decrypt, encrypt

_DEFAULT_PROFILE = "default"


def get_vault_path(vault_dir: Optional[str] = None) -> Path:
    if vault_dir:
        return Path(vault_dir)
    return Path.home() / ".envault"


def _ensure_vault_dir(vault_dir: Path) -> None:
    vault_dir.mkdir(parents=True, exist_ok=True)


def _vault_file(vault_dir: Path, profile: str) -> Path:
    return vault_dir / f"{profile}.vault"


def load_vault(vault_dir: Path, password: str, profile: str = _DEFAULT_PROFILE) -> Dict[str, Any]:
    path = _vault_file(vault_dir, profile)
    if not path.exists():
        return {}
    ciphertext = path.read_text().strip()
    plaintext = decrypt(ciphertext, password)  # raises on wrong password
    return json.loads(plaintext)


def save_vault(vault_dir: Path, data: Dict[str, Any], password: str, profile: str = _DEFAULT_PROFILE) -> None:
    _ensure_vault_dir(vault_dir)
    plaintext = json.dumps(data)
    ciphertext = encrypt(plaintext, password)
    _vault_file(vault_dir, profile).write_text(ciphertext)


def set_secret(
    vault_dir: Path,
    key: str,
    value: str,
    password: str,
    profile: str = _DEFAULT_PROFILE,
) -> None:
    data = load_vault(vault_dir, password, profile)
    data[key] = value
    save_vault(vault_dir, data, password, profile)


def get_secret(
    vault_dir: Path,
    key: str,
    password: str,
    profile: str = _DEFAULT_PROFILE,
) -> Optional[str]:
    data = load_vault(vault_dir, password, profile)
    return data.get(key)


def delete_secret(
    vault_dir: Path,
    key: str,
    password: str,
    profile: str = _DEFAULT_PROFILE,
) -> bool:
    data = load_vault(vault_dir, password, profile)
    if key not in data:
        return False
    del data[key]
    save_vault(vault_dir, data, password, profile)
    return True


def list_secrets(
    vault_dir: Path,
    password: str,
    profile: str = _DEFAULT_PROFILE,
) -> List[str]:
    data = load_vault(vault_dir, password, profile)
    return sorted(data.keys())


def re_encrypt_vault(
    vault_dir: Path,
    old_password: str,
    new_password: str,
    profile: str = _DEFAULT_PROFILE,
) -> None:
    data = load_vault(vault_dir, old_password, profile)
    save_vault(vault_dir, data, new_password, profile)
