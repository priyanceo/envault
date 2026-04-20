"""Tests for envault.access — per-key access control."""

from __future__ import annotations

import pytest

from envault.access import (
    check_permission,
    get_permissions,
    list_acl,
    remove_permissions,
    set_permissions,
)
from envault.storage import set_secret

PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def seeded_vault(vault_dir):
    set_secret("DB_URL", "postgres://localhost/db", PASSWORD, vault_dir=vault_dir)
    set_secret("API_KEY", "secret123", PASSWORD, vault_dir=vault_dir)
    return vault_dir


def test_default_permissions_are_all(seeded_vault):
    perms = get_permissions("DB_URL", PASSWORD, vault_dir=seeded_vault)
    assert perms == {"read", "write"}


def test_set_and_get_permissions(seeded_vault):
    set_permissions("DB_URL", {"read"}, PASSWORD, vault_dir=seeded_vault)
    perms = get_permissions("DB_URL", PASSWORD, vault_dir=seeded_vault)
    assert perms == {"read"}


def test_set_permissions_both(seeded_vault):
    set_permissions("API_KEY", {"read", "write"}, PASSWORD, vault_dir=seeded_vault)
    perms = get_permissions("API_KEY", PASSWORD, vault_dir=seeded_vault)
    assert perms == {"read", "write"}


def test_set_permissions_unknown_raises(seeded_vault):
    with pytest.raises(ValueError, match="Unknown permissions"):
        set_permissions("DB_URL", {"execute"}, PASSWORD, vault_dir=seeded_vault)


def test_set_permissions_missing_key_raises(vault_dir):
    with pytest.raises(KeyError, match="MISSING_KEY"):
        set_permissions("MISSING_KEY", {"read"}, PASSWORD, vault_dir=vault_dir)


def test_check_permission_allowed(seeded_vault):
    set_permissions("DB_URL", {"read"}, PASSWORD, vault_dir=seeded_vault)
    assert check_permission("DB_URL", "read", PASSWORD, vault_dir=seeded_vault) is True


def test_check_permission_denied(seeded_vault):
    set_permissions("DB_URL", {"read"}, PASSWORD, vault_dir=seeded_vault)
    assert check_permission("DB_URL", "write", PASSWORD, vault_dir=seeded_vault) is False


def test_remove_permissions_reverts_to_default(seeded_vault):
    set_permissions("DB_URL", {"read"}, PASSWORD, vault_dir=seeded_vault)
    remove_permissions("DB_URL", PASSWORD, vault_dir=seeded_vault)
    perms = get_permissions("DB_URL", PASSWORD, vault_dir=seeded_vault)
    assert perms == {"read", "write"}


def test_remove_nonexistent_acl_is_safe(seeded_vault):
    # Should not raise even if no ACL entry exists
    remove_permissions("API_KEY", PASSWORD, vault_dir=seeded_vault)


def test_list_acl_empty(seeded_vault):
    acl = list_acl(PASSWORD, vault_dir=seeded_vault)
    assert acl == {}


def test_list_acl_shows_entries(seeded_vault):
    set_permissions("DB_URL", {"read"}, PASSWORD, vault_dir=seeded_vault)
    set_permissions("API_KEY", {"read", "write"}, PASSWORD, vault_dir=seeded_vault)
    acl = list_acl(PASSWORD, vault_dir=seeded_vault)
    assert set(acl.keys()) == {"DB_URL", "API_KEY"}
    assert set(acl["DB_URL"]) == {"read"}
    assert set(acl["API_KEY"]) == {"read", "write"}
