"""Tests for envault.labels module."""

from __future__ import annotations

import pytest

from envault.storage import set_secret
from envault.labels import (
    set_label,
    get_labels,
    remove_label,
    clear_labels,
    find_by_label,
)

PASSWORD = "test-password"


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


def _seed(vault_dir, keys=("API_KEY", "DB_URL")):
    for k in keys:
        set_secret(k, f"value-{k}", PASSWORD, vault_dir=vault_dir)


def test_set_and_get_label(vault_dir):
    _seed(vault_dir)
    set_label("API_KEY", "env", "production", PASSWORD, vault_dir=vault_dir)
    labels = get_labels("API_KEY", vault_dir=vault_dir)
    assert labels["env"] == "production"


def test_get_labels_empty_when_none(vault_dir):
    _seed(vault_dir)
    assert get_labels("API_KEY", vault_dir=vault_dir) == {}


def test_set_label_missing_key_raises(vault_dir):
    with pytest.raises(KeyError):
        set_label("MISSING", "env", "prod", PASSWORD, vault_dir=vault_dir)


def test_set_multiple_labels(vault_dir):
    _seed(vault_dir)
    set_label("API_KEY", "env", "staging", PASSWORD, vault_dir=vault_dir)
    set_label("API_KEY", "team", "backend", PASSWORD, vault_dir=vault_dir)
    labels = get_labels("API_KEY", vault_dir=vault_dir)
    assert labels == {"env": "staging", "team": "backend"}


def test_remove_label_returns_true(vault_dir):
    _seed(vault_dir)
    set_label("API_KEY", "env", "prod", PASSWORD, vault_dir=vault_dir)
    assert remove_label("API_KEY", "env", vault_dir=vault_dir) is True
    assert get_labels("API_KEY", vault_dir=vault_dir) == {}


def test_remove_label_returns_false_when_absent(vault_dir):
    _seed(vault_dir)
    assert remove_label("API_KEY", "env", vault_dir=vault_dir) is False


def test_clear_labels(vault_dir):
    _seed(vault_dir)
    set_label("API_KEY", "env", "prod", PASSWORD, vault_dir=vault_dir)
    set_label("API_KEY", "tier", "free", PASSWORD, vault_dir=vault_dir)
    clear_labels("API_KEY", vault_dir=vault_dir)
    assert get_labels("API_KEY", vault_dir=vault_dir) == {}


def test_find_by_label_key_only(vault_dir):
    _seed(vault_dir)
    set_label("API_KEY", "env", "prod", PASSWORD, vault_dir=vault_dir)
    set_label("DB_URL", "env", "staging", PASSWORD, vault_dir=vault_dir)
    results = find_by_label("env", vault_dir=vault_dir)
    assert "API_KEY" in results
    assert "DB_URL" in results


def test_find_by_label_key_and_value(vault_dir):
    _seed(vault_dir)
    set_label("API_KEY", "env", "prod", PASSWORD, vault_dir=vault_dir)
    set_label("DB_URL", "env", "staging", PASSWORD, vault_dir=vault_dir)
    results = find_by_label("env", "prod", vault_dir=vault_dir)
    assert "API_KEY" in results
    assert "DB_URL" not in results


def test_find_by_label_no_match(vault_dir):
    _seed(vault_dir)
    assert find_by_label("nonexistent", vault_dir=vault_dir) == {}
