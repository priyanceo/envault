"""Tests for envault alias management."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.aliases import (
    get_alias,
    list_aliases,
    remove_alias,
    resolve,
    set_alias,
)
from envault.cli_aliases import alias_cmd


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def invoke(runner: CliRunner, vault_dir: Path, *args: str):
    return runner.invoke(alias_cmd, [*args, "--vault-dir", str(vault_dir)])


# --- Unit tests ---

def test_set_and_get_alias(vault_dir: Path) -> None:
    set_alias("db", "DATABASE_URL", vault_dir=vault_dir)
    assert get_alias("db", vault_dir=vault_dir) == "DATABASE_URL"


def test_get_alias_missing_returns_none(vault_dir: Path) -> None:
    assert get_alias("nonexistent", vault_dir=vault_dir) is None


def test_set_alias_empty_name_raises(vault_dir: Path) -> None:
    with pytest.raises(ValueError, match="Alias name"):
        set_alias("", "SOME_KEY", vault_dir=vault_dir)


def test_set_alias_empty_key_raises(vault_dir: Path) -> None:
    with pytest.raises(ValueError, match="Target key"):
        set_alias("myalias", "", vault_dir=vault_dir)


def test_remove_alias_returns_true(vault_dir: Path) -> None:
    set_alias("db", "DATABASE_URL", vault_dir=vault_dir)
    assert remove_alias("db", vault_dir=vault_dir) is True
    assert get_alias("db", vault_dir=vault_dir) is None


def test_remove_alias_missing_returns_false(vault_dir: Path) -> None:
    assert remove_alias("ghost", vault_dir=vault_dir) is False


def test_list_aliases(vault_dir: Path) -> None:
    set_alias("a", "KEY_A", vault_dir=vault_dir)
    set_alias("b", "KEY_B", vault_dir=vault_dir)
    result = list_aliases(vault_dir=vault_dir)
    assert result == {"a": "KEY_A", "b": "KEY_B"}


def test_resolve_known_alias(vault_dir: Path) -> None:
    set_alias("short", "VERY_LONG_KEY_NAME", vault_dir=vault_dir)
    assert resolve("short", vault_dir=vault_dir) == "VERY_LONG_KEY_NAME"


def test_resolve_unknown_returns_input(vault_dir: Path) -> None:
    assert resolve("RAW_KEY", vault_dir=vault_dir) == "RAW_KEY"


# --- CLI tests ---

def test_cli_set_and_get(runner: CliRunner, vault_dir: Path) -> None:
    result = invoke(runner, vault_dir, "set", "db", "DATABASE_URL")
    assert result.exit_code == 0
    assert "saved" in result.output

    result = invoke(runner, vault_dir, "get", "db")
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output


def test_cli_get_missing_exits_nonzero(runner: CliRunner, vault_dir: Path) -> None:
    result = invoke(runner, vault_dir, "get", "missing")
    assert result.exit_code != 0


def test_cli_remove(runner: CliRunner, vault_dir: Path) -> None:
    invoke(runner, vault_dir, "set", "x", "X_KEY")
    result = invoke(runner, vault_dir, "remove", "x")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_remove_missing_exits_nonzero(runner: CliRunner, vault_dir: Path) -> None:
    result = invoke(runner, vault_dir, "remove", "nope")
    assert result.exit_code != 0


def test_cli_list_empty(runner: CliRunner, vault_dir: Path) -> None:
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No aliases" in result.output


def test_cli_list_with_entries(runner: CliRunner, vault_dir: Path) -> None:
    invoke(runner, vault_dir, "set", "a", "KEY_A")
    invoke(runner, vault_dir, "set", "b", "KEY_B")
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "a -> KEY_A" in result.output
    assert "b -> KEY_B" in result.output
