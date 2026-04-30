"""CLI tests for the mentions feature."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_mentions import mentions_cmd
from envault.mentions import update_mentions


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        mentions_cmd,
        ["--vault-dir", vault_dir, *args],
        catch_exceptions=False,
    )


def test_get_shows_references(runner, vault_dir):
    update_mentions(vault_dir, "DB_URL", "${DB_USER}:${DB_PASS}")
    result = invoke(runner, vault_dir, "get", "DB_URL")
    assert result.exit_code == 0
    assert "DB_USER" in result.output
    assert "DB_PASS" in result.output


def test_get_no_references(runner, vault_dir):
    result = invoke(runner, vault_dir, "get", "PLAIN_KEY")
    assert result.exit_code == 0
    assert "references no other keys" in result.output


def test_reverse_shows_sources(runner, vault_dir):
    update_mentions(vault_dir, "A", "${SHARED}")
    update_mentions(vault_dir, "B", "${SHARED}")
    result = invoke(runner, vault_dir, "reverse", "SHARED")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_reverse_no_sources(runner, vault_dir):
    result = invoke(runner, vault_dir, "reverse", "ORPHAN")
    assert result.exit_code == 0
    assert "No keys reference" in result.output


def test_remove_existing(runner, vault_dir):
    update_mentions(vault_dir, "X", "${Y}")
    result = invoke(runner, vault_dir, "remove", "X")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_remove_missing(runner, vault_dir):
    result = invoke(runner, vault_dir, "remove", "GHOST")
    assert result.exit_code == 0
    assert "No mention records" in result.output


def test_list_all(runner, vault_dir):
    update_mentions(vault_dir, "A", "${B}")
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output


def test_list_empty(runner, vault_dir):
    result = invoke(runner, vault_dir, "list")
    assert result.exit_code == 0
    assert "No mentions" in result.output
