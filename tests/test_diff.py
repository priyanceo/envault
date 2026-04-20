"""Tests for envault.diff and cli_diff."""

import os
import pytest
from click.testing import CliRunner
from envault.storage import set_secret
from envault.diff import diff_vault_vs_file, format_diff
from envault.cli_diff import diff_cmd


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


PASSWORD = "testpass"


def _populate_vault(vault_dir, secrets):
    for k, v in secrets.items():
        set_secret(vault_dir, PASSWORD, k, v)


def _write_env(tmp_path, content, name="test.env"):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_diff_unchanged(tmp_path, vault_dir):
    _populate_vault(vault_dir, {"FOO": "bar", "BAZ": "qux"})
    env_file = _write_env(tmp_path, "FOO=bar\nBAZ=qux\n")
    entries = diff_vault_vs_file(vault_dir, PASSWORD, env_file)
    statuses = {e.key: e.status for e in entries}
    assert statuses["FOO"] == "unchanged"
    assert statuses["BAZ"] == "unchanged"


def test_diff_added_key(tmp_path, vault_dir):
    _populate_vault(vault_dir, {"FOO": "bar"})
    env_file = _write_env(tmp_path, "FOO=bar\nNEW_KEY=hello\n")
    entries = diff_vault_vs_file(vault_dir, PASSWORD, env_file)
    statuses = {e.key: e.status for e in entries}
    assert statuses["NEW_KEY"] == "added"


def test_diff_removed_key(tmp_path, vault_dir):
    _populate_vault(vault_dir, {"FOO": "bar", "OLD_KEY": "gone"})
    env_file = _write_env(tmp_path, "FOO=bar\n")
    entries = diff_vault_vs_file(vault_dir, PASSWORD, env_file)
    statuses = {e.key: e.status for e in entries}
    assert statuses["OLD_KEY"] == "removed"


def test_diff_changed_key(tmp_path, vault_dir):
    _populate_vault(vault_dir, {"FOO": "old_value"})
    env_file = _write_env(tmp_path, "FOO=new_value\n")
    entries = diff_vault_vs_file(vault_dir, PASSWORD, env_file)
    statuses = {e.key: e.status for e in entries}
    assert statuses["FOO"] == "changed"


def test_format_diff_no_values(tmp_path, vault_dir):
    _populate_vault(vault_dir, {"FOO": "old"})
    env_file = _write_env(tmp_path, "FOO=new\n")
    entries = diff_vault_vs_file(vault_dir, PASSWORD, env_file)
    output = format_diff(entries, show_values=False)
    assert "FOO" in output
    assert "old" not in output


def test_format_diff_with_values(tmp_path, vault_dir):
    _populate_vault(vault_dir, {"FOO": "old"})
    env_file = _write_env(tmp_path, "FOO=new\n")
    entries = diff_vault_vs_file(vault_dir, PASSWORD, env_file)
    output = format_diff(entries, show_values=True)
    assert "old" in output
    assert "new" in output


def test_cli_diff_exits_zero_when_identical(tmp_path, vault_dir, runner):
    _populate_vault(vault_dir, {"KEY": "val"})
    env_file = _write_env(tmp_path, "KEY=val\n")
    result = runner.invoke(
        diff_cmd,
        ["show", env_file, "--password", PASSWORD, "--vault-dir", vault_dir],
    )
    assert result.exit_code == 0
    assert "unchanged" in result.output


def test_cli_diff_exits_nonzero_when_different(tmp_path, vault_dir, runner):
    _populate_vault(vault_dir, {"KEY": "val"})
    env_file = _write_env(tmp_path, "KEY=different\n")
    result = runner.invoke(
        diff_cmd,
        ["show", env_file, "--password", PASSWORD, "--vault-dir", vault_dir],
    )
    assert result.exit_code != 0
    assert "changed" in result.output
