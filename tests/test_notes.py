"""Tests for envault.notes module."""

import os
import pytest

from envault.storage import save_vault
from envault.notes import set_note, get_note, remove_note, list_notes

PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    os.makedirs(d, exist_ok=True)
    # Seed with a couple of secrets
    save_vault(d, PASSWORD, {"API_KEY": "abc123", "DB_PASS": "secret"})
    return d


def test_set_and_get_note(vault_dir):
    set_note(vault_dir, PASSWORD, "API_KEY", "Production API key")
    note = get_note(vault_dir, PASSWORD, "API_KEY")
    assert note == "Production API key"


def test_get_note_returns_none_when_not_set(vault_dir):
    note = get_note(vault_dir, PASSWORD, "DB_PASS")
    assert note is None


def test_set_note_missing_key_raises(vault_dir):
    with pytest.raises(KeyError, match="MISSING"):
        set_note(vault_dir, PASSWORD, "MISSING", "some note")


def test_remove_note_returns_true(vault_dir):
    set_note(vault_dir, PASSWORD, "API_KEY", "to be removed")
    result = remove_note(vault_dir, PASSWORD, "API_KEY")
    assert result is True
    assert get_note(vault_dir, PASSWORD, "API_KEY") is None


def test_remove_note_returns_false_when_absent(vault_dir):
    result = remove_note(vault_dir, PASSWORD, "API_KEY")
    assert result is False


def test_list_notes_empty(vault_dir):
    notes = list_notes(vault_dir, PASSWORD)
    assert notes == {}


def test_list_notes_multiple(vault_dir):
    set_note(vault_dir, PASSWORD, "API_KEY", "note one")
    set_note(vault_dir, PASSWORD, "DB_PASS", "note two")
    notes = list_notes(vault_dir, PASSWORD)
    assert notes == {"API_KEY": "note one", "DB_PASS": "note two"}


def test_overwrite_note(vault_dir):
    set_note(vault_dir, PASSWORD, "API_KEY", "first")
    set_note(vault_dir, PASSWORD, "API_KEY", "second")
    assert get_note(vault_dir, PASSWORD, "API_KEY") == "second"
