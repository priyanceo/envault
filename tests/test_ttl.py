"""Tests for envault.ttl — TTL / expiry support."""

from __future__ import annotations

import time
import pytest

from envault.storage import set_secret
from envault.ttl import (
    get_ttl,
    is_expired,
    purge_expired,
    remove_ttl,
    set_ttl,
)

PASSWORD = "ttl-test-pass"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path / "vault")


def _seed(vault_dir: str, key: str = "API_KEY", value: str = "secret") -> None:
    set_secret(vault_dir, PASSWORD, key, value)


# ---------------------------------------------------------------------------
# set_ttl / get_ttl
# ---------------------------------------------------------------------------

def test_set_and_get_ttl(vault_dir):
    _seed(vault_dir)
    before = time.time()
    set_ttl(vault_dir, PASSWORD, "API_KEY", 300)
    expiry = get_ttl(vault_dir, PASSWORD, "API_KEY")
    assert expiry is not None
    assert expiry >= before + 300
    assert expiry <= time.time() + 301


def test_set_ttl_missing_key_raises(vault_dir):
    with pytest.raises(KeyError, match="MISSING"):
        set_ttl(vault_dir, PASSWORD, "MISSING", 60)


def test_get_ttl_no_ttl_returns_none(vault_dir):
    _seed(vault_dir)
    assert get_ttl(vault_dir, PASSWORD, "API_KEY") is None


# ---------------------------------------------------------------------------
# remove_ttl
# ---------------------------------------------------------------------------

def test_remove_ttl(vault_dir):
    _seed(vault_dir)
    set_ttl(vault_dir, PASSWORD, "API_KEY", 300)
    remove_ttl(vault_dir, PASSWORD, "API_KEY")
    assert get_ttl(vault_dir, PASSWORD, "API_KEY") is None


def test_remove_ttl_nonexistent_is_noop(vault_dir):
    _seed(vault_dir)
    remove_ttl(vault_dir, PASSWORD, "API_KEY")  # no TTL set — should not raise


# ---------------------------------------------------------------------------
# is_expired
# ---------------------------------------------------------------------------

def test_is_expired_future_ttl(vault_dir):
    _seed(vault_dir)
    set_ttl(vault_dir, PASSWORD, "API_KEY", 9999)
    assert not is_expired(vault_dir, PASSWORD, "API_KEY")


def test_is_expired_past_ttl(vault_dir):
    _seed(vault_dir)
    set_ttl(vault_dir, PASSWORD, "API_KEY", -1)  # already in the past
    assert is_expired(vault_dir, PASSWORD, "API_KEY")


def test_is_expired_no_ttl_returns_false(vault_dir):
    _seed(vault_dir)
    assert not is_expired(vault_dir, PASSWORD, "API_KEY")


# ---------------------------------------------------------------------------
# purge_expired
# ---------------------------------------------------------------------------

def test_purge_expired_removes_stale_keys(vault_dir):
    _seed(vault_dir, "OLD_KEY", "old")
    _seed(vault_dir, "NEW_KEY", "new")
    set_ttl(vault_dir, PASSWORD, "OLD_KEY", -1)   # expired
    set_ttl(vault_dir, PASSWORD, "NEW_KEY", 9999)  # still valid

    purged = purge_expired(vault_dir, PASSWORD)

    assert purged == ["OLD_KEY"]
    assert get_ttl(vault_dir, PASSWORD, "NEW_KEY") is not None


def test_purge_expired_empty_vault(vault_dir):
    purged = purge_expired(vault_dir, PASSWORD)
    assert purged == []
