"""Tests for envault.pin module."""

import time
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.pin import (
    set_pin,
    get_password_for_pin,
    clear_pin,
    is_pin_set,
    get_pin_path,
)


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def test_set_pin_creates_session_file(vault_dir):
    set_pin(vault_dir, "1234", "secret")
    assert get_pin_path(vault_dir).exists()


def test_get_password_for_correct_pin(vault_dir):
    set_pin(vault_dir, "4321", "mypassword")
    assert get_password_for_pin(vault_dir, "4321") == "mypassword"


def test_get_password_wrong_pin_raises(vault_dir):
    set_pin(vault_dir, "1234", "secret")
    with pytest.raises(PermissionError, match="Invalid PIN"):
        get_password_for_pin(vault_dir, "9999")


def test_get_password_no_session_raises(vault_dir):
    with pytest.raises(FileNotFoundError):
        get_password_for_pin(vault_dir, "1234")


def test_expired_pin_raises(vault_dir):
    set_pin(vault_dir, "1234", "secret", ttl=1)
    with patch("envault.pin.time.time", return_value=time.time() + 3600):
        with pytest.raises(PermissionError, match="expired"):
            get_password_for_pin(vault_dir, "1234")


def test_clear_pin_removes_file(vault_dir):
    set_pin(vault_dir, "1234", "secret")
    clear_pin(vault_dir)
    assert not get_pin_path(vault_dir).exists()


def test_clear_pin_no_file_does_not_raise(vault_dir):
    clear_pin(vault_dir)  # should not raise


def test_is_pin_set_true_when_active(vault_dir):
    set_pin(vault_dir, "1234", "secret")
    assert is_pin_set(vault_dir) is True


def test_is_pin_set_false_when_no_session(vault_dir):
    assert is_pin_set(vault_dir) is False


def test_is_pin_set_false_when_expired(vault_dir):
    set_pin(vault_dir, "1234", "secret", ttl=1)
    with patch("envault.pin.time.time", return_value=time.time() + 3600):
        assert is_pin_set(vault_dir) is False


def test_pin_too_short_raises(vault_dir):
    with pytest.raises(ValueError, match="at least 4 digits"):
        set_pin(vault_dir, "12", "secret")


def test_pin_non_digit_raises(vault_dir):
    with pytest.raises(ValueError, match="at least 4 digits"):
        set_pin(vault_dir, "abcd", "secret")
