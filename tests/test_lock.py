"""Tests for envault.lock session-lock functionality."""

import time
from pathlib import Path
from unittest.mock import patch

import pytest

import envault.lock as lock_mod
from envault.lock import get_remaining_ttl, is_unlocked, lock, unlock


@pytest.fixture(autouse=True)
def vault_dir(tmp_path, monkeypatch):
    vault_file = tmp_path / "vault.json"
    monkeypatch.setattr("envault.storage.get_vault_path", lambda: vault_file)
    monkeypatch.setattr("envault.lock.get_vault_path", lambda: vault_file)
    yield tmp_path


def test_unlock_creates_lock_file(vault_dir):
    unlock("secret", ttl=60)
    lock_path = vault_dir / ".session_lock"
    assert lock_path.exists()


def test_is_unlocked_returns_true_for_correct_password(vault_dir):
    unlock("mypassword", ttl=60)
    assert is_unlocked("mypassword") is True


def test_is_unlocked_returns_false_for_wrong_password(vault_dir):
    unlock("mypassword", ttl=60)
    assert is_unlocked("wrongpassword") is False


def test_is_unlocked_returns_false_when_no_lock_file(vault_dir):
    assert is_unlocked("anypassword") is False


def test_lock_removes_lock_file(vault_dir):
    unlock("secret", ttl=60)
    lock()
    lock_path = vault_dir / ".session_lock"
    assert not lock_path.exists()


def test_lock_is_idempotent_when_no_file(vault_dir):
    # Should not raise even if no lock file exists
    lock()


def test_is_unlocked_returns_false_after_expiry(vault_dir):
    unlock("secret", ttl=1)
    with patch("envault.lock.time") as mock_time:
        mock_time.time.return_value = time.time() + 10
        result = is_unlocked("secret")
    assert result is False


def test_get_remaining_ttl_returns_none_when_locked(vault_dir):
    assert get_remaining_ttl() is None


def test_get_remaining_ttl_returns_positive_value(vault_dir):
    unlock("secret", ttl=120)
    remaining = get_remaining_ttl()
    assert remaining is not None
    assert 0 < remaining <= 120


def test_get_remaining_ttl_returns_none_after_expiry(vault_dir):
    unlock("secret", ttl=1)
    with patch("envault.lock.time") as mock_time:
        mock_time.time.return_value = time.time() + 10
        remaining = get_remaining_ttl()
    assert remaining is None


def test_unlock_overwrites_existing_session(vault_dir):
    unlock("first", ttl=60)
    unlock("second", ttl=60)
    assert is_unlocked("second") is True
    assert is_unlocked("first") is False
