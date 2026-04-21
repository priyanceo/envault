"""CLI integration tests for template commands."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_templates import template_cmd
from envault.storage import set_secret


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def invoke(runner, vault_dir, args, input=None):
    env = {"ENVAULT_VAULT_DIR": str(vault_dir)}
    return runner.invoke(template_cmd, args, input=input, env=env, catch_exceptions=False)


def test_save_and_list_template(runner, vault_dir):
    result = invoke(runner, vault_dir, ["save", "myapp", "DB_URL", "SECRET_KEY"])
    assert result.exit_code == 0
    assert "myapp" in result.output

    result = invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "myapp" in result.output


def test_show_template(runner, vault_dir):
    invoke(runner, vault_dir, ["save", "svc", "PORT", "HOST"])
    result = invoke(runner, vault_dir, ["show", "svc"])
    assert result.exit_code == 0
    assert "HOST" in result.output
    assert "PORT" in result.output


def test_show_missing_template_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        template_cmd, ["show", "ghost"],
        env={"ENVAULT_VAULT_DIR": str(vault_dir)},
    )
    assert result.exit_code != 0


def test_delete_template(runner, vault_dir):
    invoke(runner, vault_dir, ["save", "tmp", "X"])
    result = invoke(runner, vault_dir, ["delete", "tmp"])
    assert result.exit_code == 0
    assert "deleted" in result.output

    result = invoke(runner, vault_dir, ["list"])
    assert "tmp" not in result.output


def test_delete_missing_template_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        template_cmd, ["delete", "nope"],
        env={"ENVAULT_VAULT_DIR": str(vault_dir)},
    )
    assert result.exit_code != 0


def test_list_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, ["list"])
    assert result.exit_code == 0
    assert "No templates" in result.output


def test_check_all_match(runner, vault_dir):
    password = "pass"
    set_secret(vault_dir, "DB_URL", "x", password)
    set_secret(vault_dir, "PORT", "8080", password)
    invoke(runner, vault_dir, ["save", "app", "DB_URL", "PORT"])
    result = invoke(runner, vault_dir, ["check", "app", "--password", password])
    assert result.exit_code == 0
    assert "All keys match" in result.output


def test_check_missing_and_extra(runner, vault_dir):
    password = "pass"
    set_secret(vault_dir, "EXTRA_KEY", "v", password)
    invoke(runner, vault_dir, ["save", "app", "DB_URL", "PORT"])
    result = invoke(runner, vault_dir, ["check", "app", "--password", password])
    assert result.exit_code == 0
    assert "Missing" in result.output
    assert "Extra" in result.output
