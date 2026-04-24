"""Tests for envault.hooks and envault.cli_hooks."""

import pytest
from click.testing import CliRunner
from envault.hooks import (
    register_hook,
    unregister_hook,
    get_hooks,
    list_hooks,
    fire_hooks,
    VALID_EVENTS,
)
from envault.cli_hooks import hooks_cmd


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args):
    return runner.invoke(hooks_cmd, ["--vault-dir", vault_dir, *args])


# --- unit tests ---

def test_register_and_get_hook(vault_dir):
    register_hook("post-set", "echo hello", vault_dir=vault_dir)
    cmds = get_hooks("post-set", vault_dir=vault_dir)
    assert "echo hello" in cmds


def test_register_duplicate_is_idempotent(vault_dir):
    register_hook("post-set", "echo hello", vault_dir=vault_dir)
    register_hook("post-set", "echo hello", vault_dir=vault_dir)
    assert get_hooks("post-set", vault_dir=vault_dir).count("echo hello") == 1


def test_register_invalid_event_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid event"):
        register_hook("on-explode", "rm -rf /", vault_dir=vault_dir)


def test_unregister_hook_returns_true(vault_dir):
    register_hook("pre-delete", "echo bye", vault_dir=vault_dir)
    result = unregister_hook("pre-delete", "echo bye", vault_dir=vault_dir)
    assert result is True
    assert get_hooks("pre-delete", vault_dir=vault_dir) == []


def test_unregister_missing_hook_returns_false(vault_dir):
    result = unregister_hook("pre-get", "nonexistent", vault_dir=vault_dir)
    assert result is False


def test_list_hooks_returns_all(vault_dir):
    register_hook("post-set", "echo a", vault_dir=vault_dir)
    register_hook("pre-get", "echo b", vault_dir=vault_dir)
    all_hooks = list_hooks(vault_dir=vault_dir)
    assert "post-set" in all_hooks
    assert "pre-get" in all_hooks


def test_fire_hooks_returns_exit_codes(vault_dir):
    register_hook("post-set", "true", vault_dir=vault_dir)
    codes = fire_hooks("post-set", vault_dir=vault_dir)
    assert codes == [0]


def test_get_hooks_no_file_returns_empty(vault_dir):
    assert get_hooks("post-delete", vault_dir=vault_dir) == []


# --- CLI tests ---

def test_cli_register_and_list(vault_dir, runner):
    r = runner.invoke(hooks_cmd, ["register", "post-set", "echo done", "--vault-dir", vault_dir])
    assert r.exit_code == 0
    assert "Hook registered" in r.output

    r2 = runner.invoke(hooks_cmd, ["list", "--vault-dir", vault_dir])
    assert "post-set" in r2.output
    assert "echo done" in r2.output


def test_cli_unregister_missing_exits_nonzero(vault_dir, runner):
    r = runner.invoke(hooks_cmd, ["unregister", "post-set", "ghost", "--vault-dir", vault_dir])
    assert r.exit_code != 0


def test_cli_list_empty(vault_dir, runner):
    r = runner.invoke(hooks_cmd, ["list", "--vault-dir", vault_dir])
    assert r.exit_code == 0
    assert "No hooks registered" in r.output


def test_cli_list_filtered_by_event(vault_dir, runner):
    runner.invoke(hooks_cmd, ["register", "pre-get", "echo pre", "--vault-dir", vault_dir])
    r = runner.invoke(hooks_cmd, ["list", "--event", "pre-get", "--vault-dir", vault_dir])
    assert "echo pre" in r.output
