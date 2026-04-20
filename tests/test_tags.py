"""Tests for envault.tags module."""

import os
import pytest

from envault.storage import set_secret
from envault.tags import (
    add_tag,
    get_tags,
    get_tags_map,
    list_by_tag,
    remove_tag,
    set_tags,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path / "vault")


def _seed(vault_dir):
    """Add a couple of secrets so the vault file exists."""
    set_secret(vault_dir, PASSWORD, "DB_URL", "postgres://localhost/db")
    set_secret(vault_dir, PASSWORD, "API_KEY", "secret-api-key")
    set_secret(vault_dir, PASSWORD, "REDIS_URL", "redis://localhost")


def test_add_and_get_tag(vault_dir):
    _seed(vault_dir)
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    assert "database" in get_tags(vault_dir, PASSWORD, "DB_URL")


def test_add_duplicate_tag_is_idempotent(vault_dir):
    _seed(vault_dir)
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    assert get_tags(vault_dir, PASSWORD, "DB_URL").count("database") == 1


def test_set_tags_replaces_existing(vault_dir):
    _seed(vault_dir)
    add_tag(vault_dir, PASSWORD, "API_KEY", "old-tag")
    set_tags(vault_dir, PASSWORD, "API_KEY", ["new-tag", "production"])
    tags = get_tags(vault_dir, PASSWORD, "API_KEY")
    assert "old-tag" not in tags
    assert "new-tag" in tags
    assert "production" in tags


def test_remove_tag(vault_dir):
    _seed(vault_dir)
    add_tag(vault_dir, PASSWORD, "DB_URL", "database")
    add_tag(vault_dir, PASSWORD, "DB_URL", "production")
    remove_tag(vault_dir, PASSWORD, "DB_URL", "database")
    tags = get_tags(vault_dir, PASSWORD, "DB_URL")
    assert "database" not in tags
    assert "production" in tags


def test_remove_absent_tag_is_noop(vault_dir):
    _seed(vault_dir)
    # Should not raise
    remove_tag(vault_dir, PASSWORD, "DB_URL", "nonexistent")
    assert get_tags(vault_dir, PASSWORD, "DB_URL") == []


def test_list_by_tag(vault_dir):
    _seed(vault_dir)
    add_tag(vault_dir, PASSWORD, "DB_URL", "infrastructure")
    add_tag(vault_dir, PASSWORD, "REDIS_URL", "infrastructure")
    add_tag(vault_dir, PASSWORD, "API_KEY", "external")
    result = list_by_tag(vault_dir, PASSWORD, "infrastructure")
    assert set(result) == {"DB_URL", "REDIS_URL"}


def test_list_by_tag_no_matches(vault_dir):
    _seed(vault_dir)
    assert list_by_tag(vault_dir, PASSWORD, "ghost") == []


def test_get_tags_map_returns_all(vault_dir):
    _seed(vault_dir)
    add_tag(vault_dir, PASSWORD, "DB_URL", "db")
    add_tag(vault_dir, PASSWORD, "API_KEY", "ext")
    tag_map = get_tags_map(vault_dir, PASSWORD)
    assert "DB_URL" in tag_map
    assert "API_KEY" in tag_map


def test_get_tags_unknown_key_returns_empty(vault_dir):
    _seed(vault_dir)
    assert get_tags(vault_dir, PASSWORD, "DOES_NOT_EXIST") == []
