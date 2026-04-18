"""Additional CLI tests for snapshot delete."""
import pytest
from click.testing import CliRunner
from envault.snapshot import create_snapshot
from envault.storage import set_secret
from envault.cli_snapshot import snapshot_cmd

PASSWORD = "pw"


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_delete_snapshot(runner, vault_dir):
    set_secret(vault_dir, PASSWORD, "K", "v")
    snap = create_snapshot(vault_dir, PASSWORD)
    r = runner.invoke(snapshot_cmd, ["--vault-dir", str(vault_dir), "delete", snap.name], catch_exceptions=False)
    assert r.exit_code == 0
    assert "Deleted" in r.output
    assert not snap.exists()


def test_cli_delete_missing_snapshot(runner, vault_dir):
    r = runner.invoke(snapshot_cmd, ["--vault-dir", str(vault_dir), "delete", "ghost.json"], catch_exceptions=False)
    assert r.exit_code == 1


def test_cli_list_empty(runner, vault_dir):
    r = runner.invoke(snapshot_cmd, ["--vault-dir", str(vault_dir), "list"], catch_exceptions=False)
    assert r.exit_code == 0
    assert "No snapshots" in r.output


def test_cli_restore_missing(runner, vault_dir):
    r = runner.invoke(snapshot_cmd, ["--vault-dir", str(vault_dir), "restore", "missing.json"], input=f"{PASSWORD}\n{PASSWORD}\n", catch_exceptions=False)
    assert r.exit_code == 1
