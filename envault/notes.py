"""Per-secret notes/annotations stored in the vault metadata."""

from __future__ import annotations

from typing import Optional

from envault.storage import load_vault, save_vault

_NOTES_KEY = "__notes__"


def _get_notes_map(vault_dir: str, password: str) -> dict:
    vault = load_vault(vault_dir, password)
    return vault.get(_NOTES_KEY, {})


def _set_notes_map(vault_dir: str, password: str, notes: dict) -> None:
    vault = load_vault(vault_dir, password)
    vault[_NOTES_KEY] = notes
    save_vault(vault_dir, password, vault)


def set_note(vault_dir: str, password: str, key: str, note: str) -> None:
    """Attach a note/annotation to a secret key."""
    vault = load_vault(vault_dir, password)
    if key not in vault:
        raise KeyError(f"Secret '{key}' does not exist.")
    notes = vault.get(_NOTES_KEY, {})
    notes[key] = note
    vault[_NOTES_KEY] = notes
    save_vault(vault_dir, password, vault)


def get_note(vault_dir: str, password: str, key: str) -> Optional[str]:
    """Retrieve the note for a secret key, or None if not set."""
    notes = _get_notes_map(vault_dir, password)
    return notes.get(key)


def remove_note(vault_dir: str, password: str, key: str) -> bool:
    """Remove the note for a secret key. Returns True if a note was removed."""
    vault = load_vault(vault_dir, password)
    notes = vault.get(_NOTES_KEY, {})
    if key not in notes:
        return False
    del notes[key]
    vault[_NOTES_KEY] = notes
    save_vault(vault_dir, password, vault)
    return True


def list_notes(vault_dir: str, password: str) -> dict:
    """Return all key -> note mappings."""
    return dict(_get_notes_map(vault_dir, password))
