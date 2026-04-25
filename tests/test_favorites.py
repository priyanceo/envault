"""Tests for envault.favorites."""

from __future__ import annotations

import pytest

from envault.storage import set_secret
from envault.favorites import (
    add_favorite,
    remove_favorite,
    list_favorites,
    is_favorite,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def _seed(vault_dir, keys):
    for k in keys:
        set_secret(vault_dir, PASSWORD, k, f"value-{k}")


def test_add_and_is_favorite(vault_dir):
    _seed(vault_dir, ["API_KEY"])
    add_favorite(vault_dir, PASSWORD, "API_KEY")
    assert is_favorite(vault_dir, "API_KEY") is True


def test_list_favorites_empty(vault_dir):
    assert list_favorites(vault_dir) == []


def test_list_favorites_sorted(vault_dir):
    _seed(vault_dir, ["ZEBRA", "ALPHA", "MIDDLE"])
    add_favorite(vault_dir, PASSWORD, "ZEBRA")
    add_favorite(vault_dir, PASSWORD, "ALPHA")
    add_favorite(vault_dir, PASSWORD, "MIDDLE")
    assert list_favorites(vault_dir) == ["ALPHA", "MIDDLE", "ZEBRA"]


def test_add_favorite_missing_key_raises(vault_dir):
    with pytest.raises(KeyError, match="MISSING"):
        add_favorite(vault_dir, PASSWORD, "MISSING")


def test_add_favorite_is_idempotent(vault_dir):
    _seed(vault_dir, ["DB_URL"])
    add_favorite(vault_dir, PASSWORD, "DB_URL")
    add_favorite(vault_dir, PASSWORD, "DB_URL")
    assert list_favorites(vault_dir).count("DB_URL") == 1


def test_remove_favorite_returns_true(vault_dir):
    _seed(vault_dir, ["TOKEN"])
    add_favorite(vault_dir, PASSWORD, "TOKEN")
    result = remove_favorite(vault_dir, "TOKEN")
    assert result is True
    assert is_favorite(vault_dir, "TOKEN") is False


def test_remove_favorite_not_present_returns_false(vault_dir):
    result = remove_favorite(vault_dir, "NONEXISTENT")
    assert result is False


def test_is_favorite_false_when_not_added(vault_dir):
    _seed(vault_dir, ["SECRET"])
    assert is_favorite(vault_dir, "SECRET") is False


def test_remove_favorite_does_not_affect_others(vault_dir):
    _seed(vault_dir, ["A", "B", "C"])
    for k in ["A", "B", "C"]:
        add_favorite(vault_dir, PASSWORD, k)
    remove_favorite(vault_dir, "B")
    assert list_favorites(vault_dir) == ["A", "C"]
