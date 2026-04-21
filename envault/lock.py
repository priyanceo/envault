"""Session lock: track whether the vault is currently 'unlocked' in memory.

The lock state is persisted to a small JSON file in the vault directory so
that CLI commands can share a single unlock session without re-prompting for
the password on every invocation within a time window.
"""

import json
import time
from pathlib import Path
from typing import Optional

from envault.storage import get_vault_path

_LOCK_FILENAME = ".session_lock"
_DEFAULT_TTL_SECONDS = 300  # 5 minutes


def _get_lock_path() -> Path:
    return get_vault_path().parent / _LOCK_FILENAME


def unlock(password: str, ttl: int = _DEFAULT_TTL_SECONDS) -> None:
    """Write a session lock file recording the password hash and expiry."""
    import hashlib

    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    expires_at = time.time() + ttl
    lock_data = {"pw_hash": pw_hash, "expires_at": expires_at}
    lock_path = _get_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(lock_data))


def lock() -> None:
    """Remove the session lock file, effectively locking the vault."""
    lock_path = _get_lock_path()
    if lock_path.exists():
        lock_path.unlink()


def is_unlocked(password: str) -> bool:
    """Return True if a valid, non-expired session exists for *password*."""
    import hashlib

    lock_path = _get_lock_path()
    if not lock_path.exists():
        return False
    try:
        data = json.loads(lock_path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    if time.time() > data.get("expires_at", 0):
        lock_path.unlink(missing_ok=True)
        return False
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    return pw_hash == data.get("pw_hash", "")


def get_remaining_ttl() -> Optional[float]:
    """Return seconds remaining in the current session, or None if locked."""
    lock_path = _get_lock_path()
    if not lock_path.exists():
        return None
    try:
        data = json.loads(lock_path.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    remaining = data.get("expires_at", 0) - time.time()
    return max(remaining, 0.0) if remaining > 0 else None
