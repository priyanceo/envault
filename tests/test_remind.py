"""Tests for envault.remind module."""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from envault.remind import (
    set_reminder,
    get_reminder,
    remove_reminder,
    get_due_reminders,
    list_reminders,
    get_reminders_path,
)


@pytest.fixture
def vault_dir(tmp_path):
    d = tmp_path / ".envault"
    d.mkdir()
    return str(d)


def _future(days=1):
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days=1):
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_set_and_get_reminder(vault_dir):
    remind_at = _future(3)
    set_reminder("MY_KEY", remind_at, vault_dir=vault_dir)
    result = get_reminder("MY_KEY", vault_dir=vault_dir)
    assert result is not None
    # Compare with second precision
    assert abs((result - remind_at).total_seconds()) < 1


def test_get_reminder_returns_none_when_not_set(vault_dir):
    assert get_reminder("NONEXISTENT", vault_dir=vault_dir) is None


def test_remove_reminder_returns_true(vault_dir):
    set_reminder("KEY", _future(), vault_dir=vault_dir)
    assert remove_reminder("KEY", vault_dir=vault_dir) is True
    assert get_reminder("KEY", vault_dir=vault_dir) is None


def test_remove_reminder_returns_false_when_missing(vault_dir):
    assert remove_reminder("GHOST", vault_dir=vault_dir) is False


def test_get_due_reminders_returns_past_only(vault_dir):
    set_reminder("PAST_KEY", _past(2), vault_dir=vault_dir)
    set_reminder("FUTURE_KEY", _future(2), vault_dir=vault_dir)
    due = get_due_reminders(vault_dir=vault_dir)
    keys = [k for k, _ in due]
    assert "PAST_KEY" in keys
    assert "FUTURE_KEY" not in keys


def test_get_due_reminders_empty_when_none_due(vault_dir):
    set_reminder("FUTURE", _future(5), vault_dir=vault_dir)
    assert get_due_reminders(vault_dir=vault_dir) == []


def test_list_reminders_sorted(vault_dir):
    set_reminder("B", _future(3), vault_dir=vault_dir)
    set_reminder("A", _future(1), vault_dir=vault_dir)
    set_reminder("C", _future(5), vault_dir=vault_dir)
    items = list_reminders(vault_dir=vault_dir)
    keys = [k for k, _ in items]
    assert keys == ["A", "B", "C"]


def test_list_reminders_empty_vault(vault_dir):
    assert list_reminders(vault_dir=vault_dir) == []


def test_reminders_file_created(vault_dir):
    set_reminder("KEY", _future(), vault_dir=vault_dir)
    path = get_reminders_path(vault_dir=vault_dir)
    assert path.exists()


def test_set_reminder_overwrites_existing(vault_dir):
    t1 = _future(1)
    t2 = _future(5)
    set_reminder("KEY", t1, vault_dir=vault_dir)
    set_reminder("KEY", t2, vault_dir=vault_dir)
    result = get_reminder("KEY", vault_dir=vault_dir)
    assert abs((result - t2).total_seconds()) < 1
