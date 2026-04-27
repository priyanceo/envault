"""Tests for envault.categories."""

import pytest

from envault.categories import (
    get_category,
    get_unique_categories,
    list_all_categories,
    list_by_category,
    remove_category,
    set_category,
)
from envault.storage import set_secret

PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path):
    return tmp_path


def _seed(vault_dir, keys):
    for key, value in keys.items():
        set_secret(key, value, PASSWORD, vault_dir=vault_dir)


def test_set_and_get_category(vault_dir):
    _seed(vault_dir, {"DB_URL": "postgres://localhost/db"})
    set_category("DB_URL", "database", PASSWORD, vault_dir=vault_dir)
    assert get_category("DB_URL", vault_dir=vault_dir) == "database"


def test_get_category_returns_none_when_not_set(vault_dir):
    _seed(vault_dir, {"API_KEY": "secret"})
    assert get_category("API_KEY", vault_dir=vault_dir) is None


def test_set_category_missing_key_raises(vault_dir):
    with pytest.raises(KeyError, match="MISSING_KEY"):
        set_category("MISSING_KEY", "infra", PASSWORD, vault_dir=vault_dir)


def test_remove_category_returns_true(vault_dir):
    _seed(vault_dir, {"TOKEN": "abc"})
    set_category("TOKEN", "auth", PASSWORD, vault_dir=vault_dir)
    result = remove_category("TOKEN", vault_dir=vault_dir)
    assert result is True
    assert get_category("TOKEN", vault_dir=vault_dir) is None


def test_remove_category_returns_false_when_not_set(vault_dir):
    _seed(vault_dir, {"TOKEN": "abc"})
    result = remove_category("TOKEN", vault_dir=vault_dir)
    assert result is False


def test_list_by_category(vault_dir):
    _seed(vault_dir, {"DB_URL": "u", "DB_PASS": "p", "API_KEY": "k"})
    set_category("DB_URL", "database", PASSWORD, vault_dir=vault_dir)
    set_category("DB_PASS", "database", PASSWORD, vault_dir=vault_dir)
    set_category("API_KEY", "auth", PASSWORD, vault_dir=vault_dir)
    result = list_by_category("database", vault_dir=vault_dir)
    assert result == ["DB_PASS", "DB_URL"]


def test_list_by_category_empty(vault_dir):
    assert list_by_category("nonexistent", vault_dir=vault_dir) == []


def test_list_all_categories(vault_dir):
    _seed(vault_dir, {"A": "1", "B": "2"})
    set_category("A", "infra", PASSWORD, vault_dir=vault_dir)
    set_category("B", "auth", PASSWORD, vault_dir=vault_dir)
    result = list_all_categories(vault_dir=vault_dir)
    assert result == {"A": "infra", "B": "auth"}


def test_get_unique_categories(vault_dir):
    _seed(vault_dir, {"X": "1", "Y": "2", "Z": "3"})
    set_category("X", "infra", PASSWORD, vault_dir=vault_dir)
    set_category("Y", "auth", PASSWORD, vault_dir=vault_dir)
    set_category("Z", "infra", PASSWORD, vault_dir=vault_dir)
    result = get_unique_categories(vault_dir=vault_dir)
    assert result == ["auth", "infra"]


def test_overwrite_category(vault_dir):
    _seed(vault_dir, {"KEY": "val"})
    set_category("KEY", "old", PASSWORD, vault_dir=vault_dir)
    set_category("KEY", "new", PASSWORD, vault_dir=vault_dir)
    assert get_category("KEY", vault_dir=vault_dir) == "new"
