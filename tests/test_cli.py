"""Tests for envault CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli import cli

PASSWORD = "cli-test-pass"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path / "vault")


def invoke(runner, vault_dir, args, input_text=None):
    return runner.invoke(cli, ["--vault-dir", vault_dir] + args, input=input_text)


def test_set_and_get_secret(runner, vault_dir):
    result = invoke(runner, vault_dir, ["set", "myapp", "DB_URL", "postgres://localhost"],
                    input_text=f"{PASSWORD}\n{PASSWORD}\n")
    assert result.exit_code == 0
    assert "Set myapp/DB_URL" in result.output

    result = invoke(runner, vault_dir, ["get", "myapp", "DB_URL"],
                    input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "postgres://localhost" in result.output


def test_get_missing_key_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, ["set", "app", "KEY", "val"],
                    input_text=f"{PASSWORD}\n{PASSWORD}\n")
    result = invoke(runner, vault_dir, ["get", "app", "MISSING"],
                    input_text=f"{PASSWORD}\n")
    assert result.exit_code != 0


def test_delete_secret(runner, vault_dir):
    invoke(runner, vault_dir, ["set", "app", "TOKEN", "abc"],
           input_text=f"{PASSWORD}\n{PASSWORD}\n")
    result = invoke(runner, vault_dir, ["delete", "app", "TOKEN"],
                    input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "Deleted app/TOKEN" in result.output


def test_delete_nonexistent_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, ["delete", "app", "GHOST"],
                    input_text=f"{PASSWORD}\n")
    assert result.exit_code != 0


def test_list_projects(runner, vault_dir):
    invoke(runner, vault_dir, ["set", "alpha", "K", "v"],
           input_text=f"{PASSWORD}\n{PASSWORD}\n")
    invoke(runner, vault_dir, ["set", "beta", "K", "v"],
           input_text=f"{PASSWORD}\n{PASSWORD}\n")
    result = invoke(runner, vault_dir, ["list"], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "alpha" in result.output
    assert "beta" in result.output


def test_list_empty_vault(runner, vault_dir):
    result = invoke(runner, vault_dir, ["list"], input_text=f"{PASSWORD}\n")
    assert result.exit_code == 0
    assert "No projects found" in result.output
