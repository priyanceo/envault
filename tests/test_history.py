"""Tests for envault history module and CLI commands."""

import time
import pytest
from pathlib import Path
from click.testing import CliRunner

from envault.history import (
    record_change,
    get_history,
    clear_history,
    list_keys_with_history,
)
from envault.cli_history import history_cmd


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, args, vault_dir):
    return runner.invoke(history_cmd, args + ["--vault-dir", str(vault_dir)])


def test_record_and_get_history(vault_dir):
    record_change("DB_PASS", "secret1", vault_dir=vault_dir)
    record_change("DB_PASS", "secret2", vault_dir=vault_dir)
    entries = get_history("DB_PASS", vault_dir=vault_dir)
    assert len(entries) == 2
    assert entries[0]["value"] == "secret1"
    assert entries[1]["value"] == "secret2"


def test_get_history_missing_key_returns_empty(vault_dir):
    entries = get_history("NONEXISTENT", vault_dir=vault_dir)
    assert entries == []


def test_history_entries_have_timestamps(vault_dir):
    before = time.time()
    record_change("API_KEY", "val", vault_dir=vault_dir)
    after = time.time()
    entries = get_history("API_KEY", vault_dir=vault_dir)
    assert before <= entries[0]["timestamp"] <= after


def test_clear_history_removes_entries(vault_dir):
    record_change("TOKEN", "abc", vault_dir=vault_dir)
    removed = clear_history("TOKEN", vault_dir=vault_dir)
    assert removed is True
    assert get_history("TOKEN", vault_dir=vault_dir) == []


def test_clear_history_missing_key_returns_false(vault_dir):
    assert clear_history("MISSING", vault_dir=vault_dir) is False


def test_list_keys_with_history(vault_dir):
    record_change("KEY_A", "v1", vault_dir=vault_dir)
    record_change("KEY_B", "v2", vault_dir=vault_dir)
    keys = list_keys_with_history(vault_dir=vault_dir)
    assert set(keys) == {"KEY_A", "KEY_B"}


def test_cli_show_history(runner, vault_dir):
    record_change("MY_KEY", "value1", vault_dir=vault_dir)
    record_change("MY_KEY", "value2", vault_dir=vault_dir)
    result = invoke(runner, ["show", "MY_KEY"], vault_dir)
    assert result.exit_code == 0
    assert "value1" in result.output
    assert "value2" in result.output


def test_cli_show_missing_key_exits_nonzero(runner, vault_dir):
    result = invoke(runner, ["show", "GHOST"], vault_dir)
    assert result.exit_code != 0


def test_cli_clear_history(runner, vault_dir):
    record_change("CLR_KEY", "val", vault_dir=vault_dir)
    result = invoke(runner, ["clear", "CLR_KEY"], vault_dir)
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_cli_list_keys(runner, vault_dir):
    record_change("ALPHA", "1", vault_dir=vault_dir)
    record_change("BETA", "2", vault_dir=vault_dir)
    result = invoke(runner, ["list"], vault_dir)
    assert result.exit_code == 0
    assert "ALPHA" in result.output
    assert "BETA" in result.output
