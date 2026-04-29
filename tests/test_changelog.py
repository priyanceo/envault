"""Tests for envault.changelog."""

import pytest
from envault.changelog import (
    record_change,
    get_changelog,
    clear_changelog,
    get_changelog_path,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_record_change_returns_entry(vault_dir):
    entry = record_change(vault_dir, action="set", key="DB_URL")
    assert entry["action"] == "set"
    assert entry["key"] == "DB_URL"
    assert "timestamp" in entry


def test_get_changelog_empty_when_no_file(vault_dir):
    assert get_changelog(vault_dir) == []


def test_record_and_retrieve_multiple(vault_dir):
    record_change(vault_dir, action="set", key="A")
    record_change(vault_dir, action="delete", key="B")
    entries = get_changelog(vault_dir)
    assert len(entries) == 2
    assert entries[0]["key"] == "A"
    assert entries[1]["action"] == "delete"


def test_filter_by_key(vault_dir):
    record_change(vault_dir, action="set", key="X")
    record_change(vault_dir, action="set", key="Y")
    record_change(vault_dir, action="rotate", key="X")
    result = get_changelog(vault_dir, key="X")
    assert len(result) == 2
    assert all(e["key"] == "X" for e in result)


def test_limit_returns_last_n(vault_dir):
    for i in range(5):
        record_change(vault_dir, action="set", key=f"K{i}")
    result = get_changelog(vault_dir, limit=3)
    assert len(result) == 3
    assert result[-1]["key"] == "K4"


def test_optional_actor_and_note(vault_dir):
    entry = record_change(vault_dir, action="set", key="SECRET", actor="alice", note="initial")
    assert entry["actor"] == "alice"
    assert entry["note"] == "initial"
    stored = get_changelog(vault_dir)
    assert stored[0]["actor"] == "alice"


def test_clear_changelog_returns_count(vault_dir):
    record_change(vault_dir, action="set", key="A")
    record_change(vault_dir, action="set", key="B")
    count = clear_changelog(vault_dir)
    assert count == 2
    assert get_changelog(vault_dir) == []


def test_record_change_empty_action_raises(vault_dir):
    with pytest.raises(ValueError, match="action"):
        record_change(vault_dir, action="", key="K")


def test_record_change_empty_key_raises(vault_dir):
    with pytest.raises(ValueError, match="key"):
        record_change(vault_dir, action="set", key="")


def test_changelog_file_created(vault_dir):
    record_change(vault_dir, action="set", key="ENV")
    assert get_changelog_path(vault_dir).exists()
