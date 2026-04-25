"""Tests for envault.bookmarks."""

from __future__ import annotations

import pytest

from envault.bookmarks import (
    add_bookmark,
    remove_bookmark,
    list_bookmarks,
    is_bookmarked,
    clear_bookmarks,
)
from envault.storage import set_secret

PASSWORD = "test-pass"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def _seed(vault_dir, keys=("ALPHA", "BETA", "GAMMA")):
    for k in keys:
        set_secret(k, f"value-{k}", PASSWORD, vault_dir=vault_dir)


def test_add_and_is_bookmark(vault_dir):
    _seed(vault_dir, ["KEY_A"])
    assert add_bookmark("KEY_A", PASSWORD, vault_dir=vault_dir) is True
    assert is_bookmarked("KEY_A", vault_dir=vault_dir) is True


def test_add_bookmark_idempotent(vault_dir):
    _seed(vault_dir, ["KEY_A"])
    add_bookmark("KEY_A", PASSWORD, vault_dir=vault_dir)
    result = add_bookmark("KEY_A", PASSWORD, vault_dir=vault_dir)
    assert result is False
    assert list_bookmarks(vault_dir=vault_dir) == ["KEY_A"]


def test_add_bookmark_missing_key_raises(vault_dir):
    with pytest.raises(KeyError):
        add_bookmark("NONEXISTENT", PASSWORD, vault_dir=vault_dir)


def test_remove_bookmark(vault_dir):
    _seed(vault_dir, ["KEY_A"])
    add_bookmark("KEY_A", PASSWORD, vault_dir=vault_dir)
    assert remove_bookmark("KEY_A", vault_dir=vault_dir) is True
    assert is_bookmarked("KEY_A", vault_dir=vault_dir) is False


def test_remove_bookmark_not_present_returns_false(vault_dir):
    assert remove_bookmark("MISSING", vault_dir=vault_dir) is False


def test_list_bookmarks_empty(vault_dir):
    assert list_bookmarks(vault_dir=vault_dir) == []


def test_list_bookmarks_sorted(vault_dir):
    _seed(vault_dir, ["ZEBRA", "ALPHA", "MANGO"])
    for k in ["ZEBRA", "ALPHA", "MANGO"]:
        add_bookmark(k, PASSWORD, vault_dir=vault_dir)
    assert list_bookmarks(vault_dir=vault_dir) == ["ALPHA", "MANGO", "ZEBRA"]


def test_clear_bookmarks(vault_dir):
    _seed(vault_dir, ["A", "B", "C"])
    for k in ["A", "B", "C"]:
        add_bookmark(k, PASSWORD, vault_dir=vault_dir)
    count = clear_bookmarks(vault_dir=vault_dir)
    assert count == 3
    assert list_bookmarks(vault_dir=vault_dir) == []


def test_clear_bookmarks_empty_vault(vault_dir):
    count = clear_bookmarks(vault_dir=vault_dir)
    assert count == 0
