"""Tests for envault.groups."""

from __future__ import annotations

import pytest

from envault.groups import (
    add_key_to_group,
    create_group,
    delete_group,
    get_group_keys,
    list_groups,
    remove_key_from_group,
)
from envault.storage import save_vault, load_vault

PASSWORD = "test-pass"


@pytest.fixture()
def vault_dir(tmp_path):
    """Return a tmp vault directory pre-seeded with a couple of secrets."""
    d = str(tmp_path)
    data = {"DB_URL": "postgres://localhost/db", "API_KEY": "abc123", "SECRET": "shh"}
    save_vault(d, PASSWORD, data)
    return d


def test_list_groups_empty(vault_dir):
    assert list_groups(vault_dir, PASSWORD) == []


def test_create_group(vault_dir):
    create_group(vault_dir, PASSWORD, "backend")
    assert "backend" in list_groups(vault_dir, PASSWORD)


def test_create_group_idempotent(vault_dir):
    create_group(vault_dir, PASSWORD, "backend")
    create_group(vault_dir, PASSWORD, "backend")  # should not raise
    assert list_groups(vault_dir, PASSWORD).count("backend") == 1


def test_delete_group_returns_true(vault_dir):
    create_group(vault_dir, PASSWORD, "backend")
    assert delete_group(vault_dir, PASSWORD, "backend") is True
    assert "backend" not in list_groups(vault_dir, PASSWORD)


def test_delete_missing_group_returns_false(vault_dir):
    assert delete_group(vault_dir, PASSWORD, "nonexistent") is False


def test_add_key_to_group(vault_dir):
    add_key_to_group(vault_dir, PASSWORD, "backend", "DB_URL")
    assert "DB_URL" in get_group_keys(vault_dir, PASSWORD, "backend")


def test_add_key_to_group_creates_group(vault_dir):
    add_key_to_group(vault_dir, PASSWORD, "new-group", "API_KEY")
    assert "new-group" in list_groups(vault_dir, PASSWORD)


def test_add_key_deduplication(vault_dir):
    add_key_to_group(vault_dir, PASSWORD, "backend", "DB_URL")
    add_key_to_group(vault_dir, PASSWORD, "backend", "DB_URL")
    assert get_group_keys(vault_dir, PASSWORD, "backend").count("DB_URL") == 1


def test_add_missing_key_raises(vault_dir):
    with pytest.raises(KeyError, match="MISSING"):
        add_key_to_group(vault_dir, PASSWORD, "backend", "MISSING")


def test_remove_key_from_group(vault_dir):
    add_key_to_group(vault_dir, PASSWORD, "backend", "API_KEY")
    result = remove_key_from_group(vault_dir, PASSWORD, "backend", "API_KEY")
    assert result is True
    assert "API_KEY" not in get_group_keys(vault_dir, PASSWORD, "backend")


def test_remove_key_not_in_group_returns_false(vault_dir):
    create_group(vault_dir, PASSWORD, "backend")
    assert remove_key_from_group(vault_dir, PASSWORD, "backend", "DB_URL") is False


def test_get_group_keys_missing_group_raises(vault_dir):
    with pytest.raises(KeyError, match="ghost"):
        get_group_keys(vault_dir, PASSWORD, "ghost")


def test_multiple_keys_in_group(vault_dir):
    for key in ("DB_URL", "API_KEY", "SECRET"):
        add_key_to_group(vault_dir, PASSWORD, "all", key)
    keys = get_group_keys(vault_dir, PASSWORD, "all")
    assert set(keys) == {"DB_URL", "API_KEY", "SECRET"}
