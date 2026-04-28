"""Tests for envault.expiry module."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone

from envault.expiry import (
    get_expiry,
    is_expired,
    list_expiring,
    remove_expiry,
    set_expiry,
)
from envault.storage import set_secret

PASSWORD = "testpass"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def _seed(vault_dir, key="API_KEY", value="secret123"):
    set_secret(vault_dir, PASSWORD, key, value)


def _future(days=1):
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days=1):
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_set_and_get_expiry(vault_dir):
    _seed(vault_dir)
    dt = _future(7)
    set_expiry(vault_dir, PASSWORD, "API_KEY", dt)
    result = get_expiry(vault_dir, "API_KEY")
    assert result is not None
    assert abs((result - dt).total_seconds()) < 1


def test_get_expiry_returns_none_when_not_set(vault_dir):
    _seed(vault_dir)
    assert get_expiry(vault_dir, "API_KEY") is None


def test_set_expiry_missing_key_raises(vault_dir):
    dt = _future()
    with pytest.raises(KeyError):
        set_expiry(vault_dir, PASSWORD, "NONEXISTENT", dt)


def test_is_expired_future_returns_false(vault_dir):
    _seed(vault_dir)
    set_expiry(vault_dir, PASSWORD, "API_KEY", _future(10))
    assert is_expired(vault_dir, "API_KEY") is False


def test_is_expired_past_returns_true(vault_dir):
    _seed(vault_dir)
    set_expiry(vault_dir, PASSWORD, "API_KEY", _past(1))
    assert is_expired(vault_dir, "API_KEY") is True


def test_is_expired_no_expiry_returns_false(vault_dir):
    _seed(vault_dir)
    assert is_expired(vault_dir, "API_KEY") is False


def test_remove_expiry_returns_true(vault_dir):
    _seed(vault_dir)
    set_expiry(vault_dir, PASSWORD, "API_KEY", _future())
    assert remove_expiry(vault_dir, "API_KEY") is True
    assert get_expiry(vault_dir, "API_KEY") is None


def test_remove_expiry_returns_false_when_not_set(vault_dir):
    _seed(vault_dir)
    assert remove_expiry(vault_dir, "API_KEY") is False


def test_list_expiring_sorted(vault_dir):
    for key in ["A", "B", "C"]:
        _seed(vault_dir, key=key, value="v")
    set_expiry(vault_dir, PASSWORD, "C", _future(3))
    set_expiry(vault_dir, PASSWORD, "A", _future(1))
    set_expiry(vault_dir, PASSWORD, "B", _future(2))
    entries = list_expiring(vault_dir)
    keys = [k for k, _ in entries]
    assert keys == ["A", "B", "C"]


def test_list_expiring_empty(vault_dir):
    assert list_expiring(vault_dir) == []
