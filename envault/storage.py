"""Local encrypted storage for envault secrets."""

import json
import os
from pathlib import Path

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_DIR = Path.home() / ".envault"
VAULT_FILE = "vault.enc"


def get_vault_path(vault_dir: Path = DEFAULT_VAULT_DIR) -> Path:
    """Return the path to the vault file."""
    return vault_dir / VAULT_FILE


def _ensure_vault_dir(vault_dir: Path) -> None:
    vault_dir.mkdir(parents=True, exist_ok=True)


def load_vault(password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> dict:
    """Load and decrypt the vault. Returns empty dict if vault doesn't exist."""
    vault_path = get_vault_path(vault_dir)
    if not vault_path.exists():
        return {}
    ciphertext = vault_path.read_text(encoding="utf-8")
    plaintext = decrypt(ciphertext, password)
    return json.loads(plaintext)


def save_vault(data: dict, password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> None:
    """Encrypt and persist the vault to disk."""
    _ensure_vault_dir(vault_dir)
    vault_path = get_vault_path(vault_dir)
    plaintext = json.dumps(data)
    ciphertext = encrypt(plaintext, password)
    vault_path.write_text(ciphertext, encoding="utf-8")


def set_secret(project: str, key: str, value: str, password: str,
               vault_dir: Path = DEFAULT_VAULT_DIR) -> None:
    """Store a key-value secret under a project namespace."""
    data = load_vault(password, vault_dir)
    data.setdefault(project, {})
    data[project][key] = value
    save_vault(data, password, vault_dir)


def get_secret(project: str, key: str, password: str,
               vault_dir: Path = DEFAULT_VAULT_DIR) -> str | None:
    """Retrieve a secret by project and key."""
    data = load_vault(password, vault_dir)
    return data.get(project, {}).get(key)


def delete_secret(project: str, key: str, password: str,
                  vault_dir: Path = DEFAULT_VAULT_DIR) -> bool:
    """Delete a secret. Returns True if it existed, False otherwise."""
    data = load_vault(password, vault_dir)
    project_data = data.get(project, {})
    if key not in project_data:
        return False
    del project_data[key]
    if not project_data:
        data.pop(project, None)
    save_vault(data, password, vault_dir)
    return True


def list_projects(password: str, vault_dir: Path = DEFAULT_VAULT_DIR) -> list[str]:
    """Return all project names stored in the vault."""
    data = load_vault(password, vault_dir)
    return list(data.keys())
