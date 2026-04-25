"""CLI tests for bookmark commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_bookmarks import bookmarks_cmd
from envault.storage import set_secret

PASSWORD = "test-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        bookmarks_cmd,
        [*args, "--vault-dir", vault_dir],
        catch_exceptions=False,
    )


def _seed(vault_dir, keys=("MY_KEY",)):
    for k in keys:
        set_secret(k, f"val-{k}", PASSWORD, vault_dir=vault_dir)


def test_add_and_list(runner, vault_dir):
    _seed(vault_dir, ["MY_KEY"])
    result = runner.invoke(
        bookmarks_cmd,
        ["add", "MY_KEY", "--password", PASSWORD, "--vault-dir", vault_dir],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Bookmarked" in result.output
    result2 = invoke(runner, vault_dir, "list")
    assert "MY_KEY" in result2.output


def test_add_missing_key_exits_nonzero(runner, vault_dir):
    result = runner.invoke(
        bookmarks_cmd,
        ["add", "GHOST", "--password", PASSWORD, "--vault-dir", vault_dir],
        catch_exceptions=False,
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_remove_bookmark(runner, vault_dir):
    _seed(vault_dir, ["MY_KEY"])
    runner.invoke(
        bookmarks_cmd,
        ["add", "MY_KEY", "--password", PASSWORD, "--vault-dir", vault_dir],
        catch_exceptions=False,
    )
    result = invoke(runner, vault_dir, "remove", "MY_KEY")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_not_bookmarked_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, "remove", "GHOST")
    assert result.exit_code != 0


def test_check_bookmarked(runner, vault_dir):
    _seed(vault_dir, ["MY_KEY"])
    runner.invoke(
        bookmarks_cmd,
        ["add", "MY_KEY", "--password", PASSWORD, "--vault-dir", vault_dir],
        catch_exceptions=False,
    )
    result = invoke(runner, vault_dir, "check", "MY_KEY")
    assert result.exit_code == 0
    assert "is bookmarked" in result.output


def test_check_not_bookmarked_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, "check", "NOPE")
    assert result.exit_code != 0


def test_clear(runner, vault_dir):
    _seed(vault_dir, ["A", "B"])
    for k in ["A", "B"]:
        runner.invoke(
            bookmarks_cmd,
            ["add", k, "--password", PASSWORD, "--vault-dir", vault_dir],
            catch_exceptions=False,
        )
    result = invoke(runner, vault_dir, "clear")
    assert result.exit_code == 0
    assert "2" in result.output
    result2 = invoke(runner, vault_dir, "list")
    assert "No bookmarks" in result2.output
