"""CLI tests for envault labels commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_labels import labels_cmd
from envault.storage import set_secret

PASSWORD = "test-password"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def invoke(runner, vault_dir, args, password=PASSWORD, input_text=None):
    env = {"ENVAULT_DIR": vault_dir, "ENVAULT_PASSWORD": password}
    return runner.invoke(labels_cmd, args, env=env, input=input_text, catch_exceptions=False)


def _seed(vault_dir, keys=("API_KEY", "DB_URL")):
    for k in keys:
        set_secret(k, f"value-{k}", PASSWORD, vault_dir=vault_dir)


def test_set_and_get_label(runner, vault_dir):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, ["set", "API_KEY", "env", "production"])
    assert result.exit_code == 0
    assert "set" in result.output

    result = invoke(runner, vault_dir, ["get", "API_KEY"])
    assert result.exit_code == 0
    assert "env=production" in result.output


def test_set_label_missing_secret_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, ["set", "MISSING", "env", "prod"])
    assert result.exit_code != 0


def test_get_labels_empty(runner, vault_dir):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, ["get", "API_KEY"])
    assert result.exit_code == 0
    assert "No labels" in result.output


def test_remove_label(runner, vault_dir):
    _seed(vault_dir)
    invoke(runner, vault_dir, ["set", "API_KEY", "env", "prod"])
    result = invoke(runner, vault_dir, ["remove", "API_KEY", "env"])
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_label_missing_exits_nonzero(runner, vault_dir):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, ["remove", "API_KEY", "env"])
    assert result.exit_code != 0


def test_clear_labels(runner, vault_dir):
    _seed(vault_dir)
    invoke(runner, vault_dir, ["set", "API_KEY", "env", "prod"])
    result = invoke(runner, vault_dir, ["clear", "API_KEY"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_find_by_label(runner, vault_dir):
    _seed(vault_dir)
    invoke(runner, vault_dir, ["set", "API_KEY", "env", "prod"])
    invoke(runner, vault_dir, ["set", "DB_URL", "env", "staging"])
    result = invoke(runner, vault_dir, ["find", "env"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_URL" in result.output


def test_find_by_label_and_value(runner, vault_dir):
    _seed(vault_dir)
    invoke(runner, vault_dir, ["set", "API_KEY", "env", "prod"])
    invoke(runner, vault_dir, ["set", "DB_URL", "env", "staging"])
    result = invoke(runner, vault_dir, ["find", "env", "prod"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_URL" not in result.output


def test_find_no_match(runner, vault_dir):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, ["find", "nonexistent"])
    assert result.exit_code == 0
    assert "No matching" in result.output
