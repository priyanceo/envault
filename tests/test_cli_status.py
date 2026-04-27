"""Tests for envault.cli_status CLI commands."""

import os
import pytest
from click.testing import CliRunner
from datetime import datetime, timezone, timedelta

from envault.cli_status import status_cmd


@pytest.fixture
def vault_dir(tmp_path):
    os.environ["ENVAULT_VAULT_DIR"] = str(tmp_path)
    yield str(tmp_path)
    os.environ.pop("ENVAULT_VAULT_DIR", None)


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        status_cmd,
        ["--vault-dir", vault_dir, "--password", "pass"] + list(args),
        catch_exceptions=False,
    )


def _seed(vault_dir, key="API_KEY", value="abc123"):
    from envault.storage import set_secret
    set_secret(vault_dir, "pass", key, value)


def test_show_existing_key(runner, vault_dir):
    _seed(vault_dir)
    result = runner.invoke(status_cmd, ["show", "API_KEY", "--vault-dir", vault_dir, "--password", "pass"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "Exists" in result.output


def test_show_missing_key(runner, vault_dir):
    result = runner.invoke(status_cmd, ["show", "GHOST", "--vault-dir", vault_dir, "--password", "pass"])
    assert result.exit_code == 0
    assert "no" in result.output


def test_check_assert_exists_passes(runner, vault_dir):
    _seed(vault_dir)
    result = runner.invoke(
        status_cmd,
        ["check", "API_KEY", "--vault-dir", vault_dir, "--password", "pass", "--assert-exists"],
    )
    assert result.exit_code == 0


def test_check_assert_exists_fails(runner, vault_dir):
    result = runner.invoke(
        status_cmd,
        ["check", "MISSING", "--vault-dir", vault_dir, "--password", "pass", "--assert-exists"],
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_check_assert_not_expired_fails(runner, vault_dir):
    _seed(vault_dir)
    past = datetime.now(timezone.utc) - timedelta(seconds=5)
    from envault.ttl import set_ttl
    set_ttl(vault_dir, "API_KEY", past)
    result = runner.invoke(
        status_cmd,
        ["check", "API_KEY", "--vault-dir", vault_dir, "--password", "pass", "--assert-not-expired"],
    )
    assert result.exit_code != 0
    assert "expired" in result.output


def test_check_no_flags_shows_status(runner, vault_dir):
    _seed(vault_dir)
    result = runner.invoke(
        status_cmd,
        ["check", "API_KEY", "--vault-dir", vault_dir, "--password", "pass"],
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output
