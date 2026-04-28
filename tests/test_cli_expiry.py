"""Tests for envault.cli_expiry CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_expiry import expiry_cmd
from envault.storage import set_secret

PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        expiry_cmd,
        ["--vault-dir", vault_dir, *args],
        catch_exceptions=False,
    )


def _seed(vault_dir, key="DB_URL", value="postgres://localhost"):
    set_secret(vault_dir, PASSWORD, key, value)


def test_set_and_get_expiry(runner, vault_dir):
    _seed(vault_dir)
    result = runner.invoke(
        expiry_cmd,
        ["set", "DB_URL", "2099-01-01T00:00:00",
         "--vault-dir", vault_dir, "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Expiry set" in result.output

    result2 = invoke(runner, vault_dir, "get", "DB_URL")
    assert result2.exit_code == 0
    assert "DB_URL" in result2.output
    assert "2099" in result2.output


def test_get_no_expiry_set(runner, vault_dir):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, "get", "DB_URL")
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_set_expiry_missing_key_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        expiry_cmd,
        ["set", "MISSING", "2099-01-01T00:00:00",
         "--vault-dir", vault_dir, "--password", PASSWORD],
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_remove_expiry(runner, vault_dir):
    _seed(vault_dir)
    runner.invoke(
        expiry_cmd,
        ["set", "DB_URL", "2099-06-01T00:00:00",
         "--vault-dir", vault_dir, "--password", PASSWORD],
        catch_exceptions=False,
    )
    result = invoke(runner, vault_dir, "remove", "DB_URL")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_list_expiring(runner, vault_dir):
    for key in ["X", "Y"]:
        _seed(vault_dir, key=key, value="val")
    for key, date in [("X", "2099-03-01T00:00:00"), ("Y", "2099-01-01T00:00:00")]:
        runner.invoke(
            expiry_cmd,
            ["set", key, date, "--vault-dir", vault_dir, "--password", PASSWORD],
            catch_exceptions=False,
        )
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "Y" in result.output
    assert "X" in result.output
    # Y should appear before X (earlier expiry)
    assert result.output.index("Y") < result.output.index("X")


def test_list_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No expiry" in result.output
