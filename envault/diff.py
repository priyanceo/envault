"""Diff utilities for comparing vault secrets against a .env file."""

from typing import Dict, List, NamedTuple
from envault.export import parse_dotenv
from envault.storage import get_secret, list_secrets


class DiffEntry(NamedTuple):
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    vault_value: str | None
    file_value: str | None


def diff_vault_vs_file(
    vault_dir: str,
    password: str,
    filepath: str,
    profile: str = "default",
) -> List[DiffEntry]:
    """Compare vault secrets against a .env file and return diff entries."""
    with open(filepath, "r") as f:
        file_secrets: Dict[str, str] = parse_dotenv(f.read())

    vault_keys = set(list_secrets(vault_dir, password, profile=profile))
    file_keys = set(file_secrets.keys())
    all_keys = vault_keys | file_keys

    entries: List[DiffEntry] = []
    for key in sorted(all_keys):
        in_vault = key in vault_keys
        in_file = key in file_keys

        vault_val = get_secret(vault_dir, password, key, profile=profile) if in_vault else None
        file_val = file_secrets.get(key)

        if in_vault and not in_file:
            status = "removed"  # present in vault, missing from file
        elif in_file and not in_vault:
            status = "added"    # present in file, missing from vault
        elif vault_val == file_val:
            status = "unchanged"
        else:
            status = "changed"

        entries.append(DiffEntry(key=key, status=status, vault_value=vault_val, file_value=file_val))

    return entries


def format_diff(entries: List[DiffEntry], show_values: bool = False) -> str:
    """Render diff entries as a human-readable string."""
    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    for entry in entries:
        sym = symbols[entry.status]
        if show_values and entry.status == "changed":
            lines.append(f"{sym} {entry.key}  (vault={entry.vault_value!r} | file={entry.file_value!r})")
        else:
            lines.append(f"{sym} {entry.key}")
    return "\n".join(lines) if lines else "(no keys found)"
