"""Snapshot/backup and restore for vault secrets."""
from __future__ import annotations
import json
import time
from pathlib import Path
from envault.storage import load_vault, save_vault


def get_snapshot_dir(vault_dir: Path) -> Path:
    snap_dir = vault_dir / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    return snap_dir


def create_snapshot(vault_dir: Path, password: str, label: str = "") -> Path:
    """Dump current vault secrets to a timestamped snapshot file."""
    secrets = load_vault(vault_dir, password)
    snap_dir = get_snapshot_dir(vault_dir)
    ts = int(time.time())
    name = f"{ts}_{label}.json" if label else f"{ts}.json"
    snap_path = snap_dir / name
    snap_path.write_text(json.dumps({"ts": ts, "label": label, "secrets": secrets}, indent=2))
    return snap_path


def list_snapshots(vault_dir: Path) -> list[dict]:
    """Return metadata for all snapshots, newest first."""
    snap_dir = get_snapshot_dir(vault_dir)
    results = []
    for f in sorted(snap_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            results.append({"file": f.name, "ts": data.get("ts"), "label": data.get("label", ""), "count": len(data.get("secrets", {}))})
        except Exception:
            pass
    return results


def restore_snapshot(vault_dir: Path, password: str, filename: str) -> int:
    """Restore secrets from a snapshot file. Returns number of secrets restored."""
    snap_path = get_snapshot_dir(vault_dir) / filename
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot not found: {filename}")
    data = json.loads(snap_path.read_text())
    secrets = data.get("secrets", {})
    save_vault(vault_dir, password, secrets)
    return len(secrets)


def delete_snapshot(vault_dir: Path, filename: str) -> None:
    snap_path = get_snapshot_dir(vault_dir) / filename
    if not snap_path.exists():
        raise FileNotFoundError(f"Snapshot not found: {filename}")
    snap_path.unlink()
