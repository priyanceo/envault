"""Tests for envault.watchlist and CLI."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.watchlist import (
    watch_key,
    unwatch_key,
    is_watched,
    get_watch_reason,
    list_watched,
    clear_watchlist,
)
from envault.cli_watchlist import watchlist_cmd


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, *args, vault_dir):
    return runner.invoke(watchlist_cmd, list(args) + ["--vault-dir", vault_dir])


# --- unit tests ---

def test_watch_and_is_watched(vault_dir):
    watch_key("SECRET_KEY", reason="sensitive", vault_dir=vault_dir)
    assert is_watched("SECRET_KEY", vault_dir=vault_dir)


def test_is_watched_returns_false_when_absent(vault_dir):
    assert not is_watched("MISSING", vault_dir=vault_dir)


def test_get_watch_reason(vault_dir):
    watch_key("DB_PASS", reason="production db", vault_dir=vault_dir)
    assert get_watch_reason("DB_PASS", vault_dir=vault_dir) == "production db"


def test_get_watch_reason_returns_none_when_not_watched(vault_dir):
    assert get_watch_reason("NOPE", vault_dir=vault_dir) is None


def test_unwatch_returns_true_when_present(vault_dir):
    watch_key("X", vault_dir=vault_dir)
    assert unwatch_key("X", vault_dir=vault_dir) is True
    assert not is_watched("X", vault_dir=vault_dir)


def test_unwatch_returns_false_when_absent(vault_dir):
    assert unwatch_key("GHOST", vault_dir=vault_dir) is False


def test_list_watched_sorted(vault_dir):
    watch_key("B_KEY", reason="b", vault_dir=vault_dir)
    watch_key("A_KEY", reason="a", vault_dir=vault_dir)
    entries = list_watched(vault_dir=vault_dir)
    assert [e["key"] for e in entries] == ["A_KEY", "B_KEY"]


def test_clear_watchlist(vault_dir):
    watch_key("K1", vault_dir=vault_dir)
    watch_key("K2", vault_dir=vault_dir)
    count = clear_watchlist(vault_dir=vault_dir)
    assert count == 2
    assert list_watched(vault_dir=vault_dir) == []


# --- CLI tests ---

def test_cli_watch_and_list(runner, vault_dir):
    res = invoke(runner, "watch", "API_KEY", "--reason", "external api", vault_dir=vault_dir)
    assert res.exit_code == 0
    res2 = invoke(runner, "list", vault_dir=vault_dir)
    assert "API_KEY" in res2.output
    assert "external api" in res2.output


def test_cli_check_watched(runner, vault_dir):
    watch_key("TOKEN", reason="auth", vault_dir=vault_dir)
    res = invoke(runner, "check", "TOKEN", vault_dir=vault_dir)
    assert res.exit_code == 0
    assert "watched" in res.output


def test_cli_check_not_watched_exits_nonzero(runner, vault_dir):
    res = invoke(runner, "check", "UNKNOWN", vault_dir=vault_dir)
    assert res.exit_code != 0


def test_cli_unwatch_missing_exits_nonzero(runner, vault_dir):
    res = invoke(runner, "unwatch", "NOPE", vault_dir=vault_dir)
    assert res.exit_code != 0


def test_cli_clear(runner, vault_dir):
    watch_key("X", vault_dir=vault_dir)
    res = invoke(runner, "clear", vault_dir=vault_dir)
    assert res.exit_code == 0
    assert "1" in res.output
