"""Tests for envault.status module."""

import os
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from envault.status import get_key_status, format_status, KeyStatus


@pytest.fixture
def vault_dir(tmp_path):
    os.environ["ENVAULT_VAULT_DIR"] = str(tmp_path)
    yield str(tmp_path)
    os.environ.pop("ENVAULT_VAULT_DIR", None)


def _seed(vault_dir, password="pass", key="MY_KEY", value="secret"):
    from envault.storage import set_secret
    set_secret(vault_dir, password, key, value)


def test_get_key_status_missing_key(vault_dir):
    status = get_key_status(vault_dir, "pass", "MISSING")
    assert status.key == "MISSING"
    assert not status.exists
    assert not status.expired
    assert status.ttl_expires_at is None
    assert status.permissions == []


def test_get_key_status_existing_key(vault_dir):
    _seed(vault_dir)
    status = get_key_status(vault_dir, "pass", "MY_KEY")
    assert status.key == "MY_KEY"
    assert status.exists
    assert not status.expired


def test_get_key_status_expired_key(vault_dir):
    _seed(vault_dir)
    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    from envault.ttl import set_ttl
    set_ttl(vault_dir, "MY_KEY", past)
    status = get_key_status(vault_dir, "pass", "MY_KEY")
    assert status.expired
    assert status.ttl_expires_at is not None


def test_get_key_status_with_reminder(vault_dir):
    _seed(vault_dir)
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    from envault.remind import set_reminder
    set_reminder(vault_dir, "MY_KEY", past, "rotate me")
    status = get_key_status(vault_dir, "pass", "MY_KEY")
    assert status.reminder_due
    assert status.reminder_message == "rotate me"


def test_format_status_existing(vault_dir):
    _seed(vault_dir)
    status = get_key_status(vault_dir, "pass", "MY_KEY")
    output = format_status(status)
    assert "MY_KEY" in output
    assert "Exists" in output
    assert "Expired" in output
    assert "Perms" in output


def test_format_status_missing_key(vault_dir):
    status = get_key_status(vault_dir, "pass", "NOPE")
    output = format_status(status)
    assert "no" in output
    assert "Exists" in output
    # Should not show TTL/Perms lines for missing keys
    assert "Expired" not in output


def test_key_status_dataclass_defaults():
    ks = KeyStatus(key="X", exists=True)
    assert ks.permissions == []
    assert not ks.expired
    assert ks.ttl_expires_at is None
    assert not ks.reminder_due
