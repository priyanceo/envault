"""Unit tests for envault/templates.py."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.templates import (
    check_template,
    delete_template,
    get_template,
    list_templates,
    save_template,
)


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_save_and_get_template(vault_dir):
    save_template(vault_dir, "web", ["DB_URL", "SECRET_KEY", "PORT"])
    keys = get_template(vault_dir, "web")
    assert keys == ["DB_URL", "PORT", "SECRET_KEY"]  # sorted


def test_get_missing_template_returns_none(vault_dir):
    assert get_template(vault_dir, "nonexistent") is None


def test_save_template_deduplicates_keys(vault_dir):
    save_template(vault_dir, "dup", ["A", "A", "B"])
    assert get_template(vault_dir, "dup") == ["A", "B"]


def test_save_template_empty_keys_raises(vault_dir):
    with pytest.raises(ValueError, match="at least one key"):
        save_template(vault_dir, "empty", [])


def test_list_templates_empty(vault_dir):
    assert list_templates(vault_dir) == []


def test_list_templates_multiple(vault_dir):
    save_template(vault_dir, "beta", ["X"])
    save_template(vault_dir, "alpha", ["Y"])
    assert list_templates(vault_dir) == ["alpha", "beta"]


def test_delete_existing_template(vault_dir):
    save_template(vault_dir, "tpl", ["K"])
    assert delete_template(vault_dir, "tpl") is True
    assert get_template(vault_dir, "tpl") is None


def test_delete_missing_template_returns_false(vault_dir):
    assert delete_template(vault_dir, "ghost") is False


def test_check_template_all_match(vault_dir):
    save_template(vault_dir, "app", ["A", "B", "C"])
    result = check_template(vault_dir, "app", ["A", "B", "C"])
    assert result == {"missing": [], "extra": []}


def test_check_template_missing_keys(vault_dir):
    save_template(vault_dir, "app", ["A", "B", "C"])
    result = check_template(vault_dir, "app", ["A"])
    assert result["missing"] == ["B", "C"]
    assert result["extra"] == []


def test_check_template_extra_keys(vault_dir):
    save_template(vault_dir, "app", ["A"])
    result = check_template(vault_dir, "app", ["A", "Z"])
    assert result["missing"] == []
    assert result["extra"] == ["Z"]


def test_check_template_not_found_raises(vault_dir):
    with pytest.raises(KeyError, match="not found"):
        check_template(vault_dir, "missing", ["A"])
