"""Tests for envault.priority module."""

import pytest
from pathlib import Path

from envault.storage import set_secret
from envault.priority import (
    set_priority,
    get_priority,
    remove_priority,
    list_by_priority,
    get_all_priorities,
)

PASSWORD = "test-password"


@pytest.fixture
def vault_dir(tmp_path):
    set_secret(tmp_path, PASSWORD, "API_KEY", "abc123")
    set_secret(tmp_path, PASSWORD, "DB_PASS", "secret")
    set_secret(tmp_path, PASSWORD, "TOKEN", "tok")
    return tmp_path


def test_set_and_get_priority(vault_dir):
    set_priority(vault_dir, PASSWORD, "API_KEY", "high")
    assert get_priority(vault_dir, "API_KEY") == "high"


def test_get_priority_returns_none_when_not_set(vault_dir):
    assert get_priority(vault_dir, "API_KEY") is None


def test_set_priority_invalid_value_raises(vault_dir):
    with pytest.raises(ValueError, match="Invalid priority"):
        set_priority(vault_dir, PASSWORD, "API_KEY", "urgent")


def test_set_priority_missing_key_raises(vault_dir):
    with pytest.raises(KeyError):
        set_priority(vault_dir, PASSWORD, "NONEXISTENT", "low")


def test_remove_priority_returns_true(vault_dir):
    set_priority(vault_dir, PASSWORD, "API_KEY", "low")
    assert remove_priority(vault_dir, "API_KEY") is True
    assert get_priority(vault_dir, "API_KEY") is None


def test_remove_priority_returns_false_when_not_set(vault_dir):
    assert remove_priority(vault_dir, "API_KEY") is False


def test_list_by_priority(vault_dir):
    set_priority(vault_dir, PASSWORD, "API_KEY", "high")
    set_priority(vault_dir, PASSWORD, "TOKEN", "high")
    set_priority(vault_dir, PASSWORD, "DB_PASS", "low")
    result = list_by_priority(vault_dir, "high")
    assert result == ["API_KEY", "TOKEN"]


def test_list_by_priority_invalid_raises(vault_dir):
    with pytest.raises(ValueError):
        list_by_priority(vault_dir, "extreme")


def test_get_all_priorities_sorted_by_level_desc(vault_dir):
    set_priority(vault_dir, PASSWORD, "DB_PASS", "low")
    set_priority(vault_dir, PASSWORD, "API_KEY", "critical")
    set_priority(vault_dir, PASSWORD, "TOKEN", "medium")
    result = get_all_priorities(vault_dir)
    keys = list(result.keys())
    assert keys[0] == "API_KEY"   # critical first
    assert keys[1] == "TOKEN"     # medium second
    assert keys[2] == "DB_PASS"   # low last


def test_get_all_priorities_empty(vault_dir):
    assert get_all_priorities(vault_dir) == {}


def test_overwrite_priority(vault_dir):
    set_priority(vault_dir, PASSWORD, "API_KEY", "low")
    set_priority(vault_dir, PASSWORD, "API_KEY", "critical")
    assert get_priority(vault_dir, "API_KEY") == "critical"
