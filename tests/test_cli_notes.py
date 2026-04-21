"""Tests for the notes CLI commands."""

import os
import pytest
from click.testing import CliRunner

from envault.cli_notes import notes_cmd
from envault.storage import save_vault

PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    os.makedirs(d, exist_ok=True)
    save_vault(d, PASSWORD, {"TOKEN": "xyz", "SECRET": "shh"})
    return d


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        notes_cmd,
        list(args) + ["--vault-dir", vault_dir, "--password", PASSWORD],
    )


def test_set_and_get_note(runner, vault_dir):
    result = invoke(runner, vault_dir, "set", "TOKEN", "My API token")
    assert result.exit_code == 0
    assert "Note set for 'TOKEN'" in result.output

    result = invoke(runner, vault_dir, "get", "TOKEN")
    assert result.exit_code == 0
    assert "My API token" in result.output


def test_get_missing_note_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, "get", "TOKEN")
    assert result.exit_code != 0


def test_set_note_missing_key_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, "set", "NONEXISTENT", "oops")
    assert result.exit_code != 0


def test_remove_existing_note(runner, vault_dir):
    invoke(runner, vault_dir, "set", "SECRET", "to remove")
    result = invoke(runner, vault_dir, "remove", "SECRET")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_absent_note(runner, vault_dir):
    result = invoke(runner, vault_dir, "remove", "TOKEN")
    assert result.exit_code == 0
    assert "No note to remove" in result.output


def test_list_notes_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No notes found" in result.output


def test_list_notes_shows_all(runner, vault_dir):
    invoke(runner, vault_dir, "set", "TOKEN", "note A")
    invoke(runner, vault_dir, "set", "SECRET", "note B")
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "TOKEN" in result.output
    assert "SECRET" in result.output
