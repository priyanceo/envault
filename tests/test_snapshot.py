"""Tests for snapshot module."""
import pytest
import time
from pathlib import Path
from click.testing import CliRunner
from envault.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot
from envault.storage import set_secret, get_secret
from envault.cli_snapshot import snapshot_cmd

PASSWORD = "testpass"


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args, input=None):
    return runner.invoke(snapshot_cmd, ["--vault-dir", str(vault_dir), *args], input=input, catch_exceptions=False)


def test_create_snapshot_returns_path(vault_dir):
    set_secret(vault_dir, PASSWORD, "KEY", "val")
    path = create_snapshot(vault_dir, PASSWORD, label="v1")
    assert path.exists()
    assert "v1" in path.name


def test_list_snapshots_empty(vault_dir):
    snaps = list_snapshots(vault_dir)
    assert snaps == []


def test_list_snapshots_shows_entries(vault_dir):
    set_secret(vault_dir, PASSWORD, "A", "1")
    create_snapshot(vault_dir, PASSWORD, label="first")
    time.sleep(0.01)
    create_snapshot(vault_dir, PASSWORD, label="second")
    snaps = list_snapshots(vault_dir)
    assert len(snaps) == 2
    assert snaps[0]["label"] == "second"  # newest first


def test_restore_snapshot(vault_dir):
    set_secret(vault_dir, PASSWORD, "FOO", "bar")
    snap = create_snapshot(vault_dir, PASSWORD)
    set_secret(vault_dir, PASSWORD, "FOO", "changed")
    count = restore_snapshot(vault_dir, PASSWORD, snap.name)
    assert count == 1
    assert get_secret(vault_dir, PASSWORD, "FOO") == "bar"


def test_restore_missing_snapshot_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        restore_snapshot(vault_dir, PASSWORD, "nonexistent.json")


def test_delete_snapshot(vault_dir):
    set_secret(vault_dir, PASSWORD, "X", "y")
    snap = create_snapshot(vault_dir, PASSWORD)
    delete_snapshot(vault_dir, snap.name)
    assert not snap.exists()


def test_cli_create_and_list(runner, vault_dir):
    set_secret(vault_dir, PASSWORD, "CLI_KEY", "val")
    r = invoke(runner, vault_dir, "create", "--label", "mylabel", input=f"{PASSWORD}\n{PASSWORD}\n")
    assert r.exit_code == 0
    assert "mylabel" in r.output
    r2 = invoke(runner, vault_dir, "list")
    assert "mylabel" in r2.output


def test_cli_restore(runner, vault_dir):
    set_secret(vault_dir, PASSWORD, "R", "original")
    snap = create_snapshot(vault_dir, PASSWORD)
    set_secret(vault_dir, PASSWORD, "R", "modified")
    r = invoke(runner, vault_dir, "restore", snap.name, input=f"{PASSWORD}\n{PASSWORD}\n")
    assert r.exit_code == 0
    assert "Restored" in r.output
