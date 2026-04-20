"""CLI integration tests for the access control commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_access import access_cmd
from envault.storage import set_secret

PASSWORD = "test-password"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def seeded(vault_dir):
    set_secret("DB_URL", "postgres://localhost/db", PASSWORD, vault_dir=vault_dir)
    set_secret("API_KEY", "secret123", PASSWORD, vault_dir=vault_dir)
    return vault_dir


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        access_cmd,
        list(args),
        obj={"vault_dir": vault_dir},
        catch_exceptions=False,
    )


def test_set_and_get_permissions(runner, seeded):
    result = invoke(runner, seeded, "set", "DB_URL", "--perms", "read", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "read" in result.output

    result = invoke(runner, seeded, "get", "DB_URL", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "read" in result.output


def test_set_unknown_permission_fails(runner, seeded):
    result = invoke(runner, seeded, "set", "DB_URL", "--perms", "execute", "--password", PASSWORD)
    assert result.exit_code != 0
    assert "Error" in result.output


def test_set_missing_key_fails(runner, vault_dir):
    result = invoke(runner, vault_dir, "set", "GHOST", "--perms", "read", "--password", PASSWORD)
    assert result.exit_code != 0


def test_check_allowed(runner, seeded):
    invoke(runner, seeded, "set", "DB_URL", "--perms", "read", "--password", PASSWORD)
    result = invoke(runner, seeded, "check", "DB_URL", "read", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "ALLOWED" in result.output


def test_check_denied(runner, seeded):
    invoke(runner, seeded, "set", "DB_URL", "--perms", "read", "--password", PASSWORD)
    result = invoke(runner, seeded, "check", "DB_URL", "write", "--password", PASSWORD)
    assert result.exit_code != 0
    assert "DENIED" in result.output


def test_remove_and_list(runner, seeded):
    invoke(runner, seeded, "set", "DB_URL", "--perms", "read", "--password", PASSWORD)
    result = invoke(runner, seeded, "list", "--password", PASSWORD)
    assert "DB_URL" in result.output

    invoke(runner, seeded, "remove", "DB_URL", "--password", PASSWORD)
    result = invoke(runner, seeded, "list", "--password", PASSWORD)
    assert "No explicit ACL" in result.output


def test_list_empty(runner, seeded):
    result = invoke(runner, seeded, "list", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "No explicit ACL" in result.output
