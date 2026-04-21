"""PIN-based quick unlock for envault vault sessions."""

import hashlib
import json
import os
import time
from pathlib import Path

DEFAULT_PIN_TTL = 3600  # 1 hour


def get_pin_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".pin_session"


def _hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def set_pin(vault_dir: str, pin: str, password: str, ttl: int = DEFAULT_PIN_TTL) -> None:
    """Store a PIN session that maps to the vault password."""
    if not pin.isdigit() or len(pin) < 4:
        raise ValueError("PIN must be at least 4 digits")
    session = {
        "pin_hash": _hash_pin(pin),
        "password": password,
        "expires_at": time.time() + ttl,
    }
    path = get_pin_path(vault_dir)
    path.write_text(json.dumps(session))
    path.chmod(0o600)


def get_password_for_pin(vault_dir: str, pin: str) -> str:
    """Retrieve the vault password for a given PIN, if valid and not expired."""
    path = get_pin_path(vault_dir)
    if not path.exists():
        raise FileNotFoundError("No PIN session found")
    session = json.loads(path.read_text())
    if time.time() > session["expires_at"]:
        path.unlink(missing_ok=True)
        raise PermissionError("PIN session has expired")
    if _hash_pin(pin) != session["pin_hash"]:
        raise PermissionError("Invalid PIN")
    return session["password"]


def clear_pin(vault_dir: str) -> None:
    """Remove the PIN session file."""
    get_pin_path(vault_dir).unlink(missing_ok=True)


def is_pin_set(vault_dir: str) -> bool:
    """Return True if a non-expired PIN session exists."""
    path = get_pin_path(vault_dir)
    if not path.exists():
        return False
    try:
        session = json.loads(path.read_text())
        if time.time() > session["expires_at"]:
            path.unlink(missing_ok=True)
            return False
        return True
    except (json.JSONDecodeError, KeyError):
        return False
