"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

AUDIT_FILENAME = "audit.log"


def get_audit_path(vault_dir: Optional[Path] = None) -> Path:
    if vault_dir is None:
        vault_dir = Path.home() / ".envault"
    return vault_dir / AUDIT_FILENAME


def log_event(action: str, key: Optional[str] = None, vault_dir: Optional[Path] = None) -> None:
    """Append a JSON audit event to the audit log."""
    audit_path = get_audit_path(vault_dir)
    audit_path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
    }
    if key is not None:
        event["key"] = key

    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def read_events(vault_dir: Optional[Path] = None) -> list[dict]:
    """Read all audit events from the log file."""
    audit_path = get_audit_path(vault_dir)
    if not audit_path.exists():
        return []
    events = []
    with audit_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def clear_audit_log(vault_dir: Optional[Path] = None) -> None:
    """Delete the audit log file."""
    audit_path = get_audit_path(vault_dir)
    if audit_path.exists():
        audit_path.unlink()
