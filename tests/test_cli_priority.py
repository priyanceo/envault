"""Tests for the priority CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.storage import set_secret
from envault.cli_priority import priority_cmd

PASSWORD = "test-password"


@pytest.fixture
def vault_dir(tmp_path):
    set_secret(tmp_path, PASSWORD, "API_KEY", "abc123")
    set_secret(tmp_path, PASSWORD, "DB_PASS", "secret")
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, vault_dir, args, password=PASSWORD):
    env = {"ENVAULT_DIR": str(vault_dir), "ENVAULT_PASSWORD": password}
    return runner.invoke(priority_cmd, args, env=env, catch_exceptions=False)


def test_set_and_get_priority(runner, vault_dir):
    result = invoke(runner, vault_dir, ["set", "API_KEY", "high"])
    assert result.exit_code == 0
    assert "high" in result.output

    result = invoke(runner, vault_dir, ["get", "API_KEY"])
    assert result.exit_code == 0
    assert "high" in result.output


def test_get_priority_not_set(runner, vault_dir):
    result = invoke(runner, vault_dir, ["get", "API_KEY"])
    assert result.exit_code == 0
    assert "No priority" in result.output


def test_set_missing_key_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        priority_cmd,
        ["set", "GHOST", "low"],
        env={"ENVAULT_DIR": str(vault_dir), "ENVAULT_PASSWORD": PASSWORD},
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_remove_priority(runner, vault_dir):
    invoke(runner, vault_dir, ["set", "API_KEY", "medium"])
    result = invoke(runner, vault_dir, ["remove", "API_KEY"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_priority_not_set(runner, vault_dir):
    result = invoke(runner, vault_dir, ["remove", "API_KEY"])
    assert result.exit_code == 0
    assert "No priority" in result.output


def test_list_all_priorities(runner, vault_dir):
    invoke(runner, vault_dir, ["set", "API_KEY", "critical"])
    invoke(runner, vault_dir, ["set", "DB_PASS", "low"])
    result = invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "critical" in result.output
    assert "DB_PASS" in result.output
    assert "low" in result.output


def test_list_with_filter(runner, vault_dir):
    invoke(runner, vault_dir, ["set", "API_KEY", "high"])
    invoke(runner, vault_dir, ["set", "DB_PASS", "low"])
    result = invoke(runner, vault_dir, ["list", "--filter", "high"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_PASS" not in result.output


def test_list_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "No priorities" in result.output
