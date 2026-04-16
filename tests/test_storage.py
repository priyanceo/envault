"""Tests for envault.storage module."""

import pytest
from pathlib import Path

from envault.storage import (
    load_vault,
    save_vault,
    set_secret,
    get_secret,
    delete_secret,
    list_projects,
)

PASSWORD = "test-password-123"


@pytest.fixture
def vault_dir(tmp_path):
    return tmp_path / "vault"


def test_load_vault_returns_empty_when_missing(vault_dir):
    result = load_vault(PASSWORD, vault_dir)
    assert result == {}


def test_save_and_load_vault_roundtrip(vault_dir):
    data = {"myapp": {"DB_URL": "postgres://localhost/db"}}
    save_vault(data, PASSWORD, vault_dir)
    loaded = load_vault(PASSWORD, vault_dir)
    assert loaded == data


def test_load_vault_wrong_password_raises(vault_dir):
    save_vault({"app": {"KEY": "val"}}, PASSWORD, vault_dir)
    with pytest.raises(Exception):
        load_vault("wrong-password", vault_dir)


def test_set_and_get_secret(vault_dir):
    set_secret("myapp", "API_KEY", "abc123", PASSWORD, vault_dir)
    value = get_secret("myapp", "API_KEY", PASSWORD, vault_dir)
    assert value == "abc123"


def test_get_secret_missing_key_returns_none(vault_dir):
    result = get_secret("nonexistent", "KEY", PASSWORD, vault_dir)
    assert result is None


def test_set_secret_overwrites_existing(vault_dir):
    set_secret("app", "TOKEN", "old", PASSWORD, vault_dir)
    set_secret("app", "TOKEN", "new", PASSWORD, vault_dir)
    assert get_secret("app", "TOKEN", PASSWORD, vault_dir) == "new"


def test_delete_secret_existing(vault_dir):
    set_secret("app", "KEY", "value", PASSWORD, vault_dir)
    result = delete_secret("app", "KEY", PASSWORD, vault_dir)
    assert result is True
    assert get_secret("app", "KEY", PASSWORD, vault_dir) is None


def test_delete_secret_removes_empty_project(vault_dir):
    set_secret("app", "KEY", "value", PASSWORD, vault_dir)
    delete_secret("app", "KEY", PASSWORD, vault_dir)
    assert "app" not in list_projects(PASSWORD, vault_dir)


def test_delete_secret_nonexistent_returns_false(vault_dir):
    result = delete_secret("app", "MISSING", PASSWORD, vault_dir)
    assert result is False


def test_list_projects(vault_dir):
    set_secret("alpha", "K", "v", PASSWORD, vault_dir)
    set_secret("beta", "K", "v", PASSWORD, vault_dir)
    projects = list_projects(PASSWORD, vault_dir)
    assert set(projects) == {"alpha", "beta"}
