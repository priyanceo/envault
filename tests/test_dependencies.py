"""Tests for envault.dependencies."""

import pytest

from envault.dependencies import (
    add_dependency,
    get_dependencies,
    get_dependents,
    remove_all_for_key,
    remove_dependency,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_add_and_get_dependents(vault_dir):
    add_dependency("DB_URL", "DB_PASSWORD", vault_dir=vault_dir)
    assert get_dependents("DB_PASSWORD", vault_dir=vault_dir) == ["DB_URL"]


def test_get_dependents_empty_when_none(vault_dir):
    assert get_dependents("MISSING_KEY", vault_dir=vault_dir) == []


def test_add_dependency_is_idempotent(vault_dir):
    add_dependency("APP_KEY", "SECRET", vault_dir=vault_dir)
    add_dependency("APP_KEY", "SECRET", vault_dir=vault_dir)
    assert get_dependents("SECRET", vault_dir=vault_dir) == ["APP_KEY"]


def test_multiple_dependents(vault_dir):
    add_dependency("A", "BASE", vault_dir=vault_dir)
    add_dependency("B", "BASE", vault_dir=vault_dir)
    dependents = get_dependents("BASE", vault_dir=vault_dir)
    assert set(dependents) == {"A", "B"}


def test_get_dependencies(vault_dir):
    add_dependency("CHILD", "PARENT1", vault_dir=vault_dir)
    add_dependency("CHILD", "PARENT2", vault_dir=vault_dir)
    deps = get_dependencies("CHILD", vault_dir=vault_dir)
    assert set(deps) == {"PARENT1", "PARENT2"}


def test_get_dependencies_empty_when_none(vault_dir):
    assert get_dependencies("ORPHAN", vault_dir=vault_dir) == []


def test_remove_dependency_returns_true(vault_dir):
    add_dependency("X", "Y", vault_dir=vault_dir)
    assert remove_dependency("X", "Y", vault_dir=vault_dir) is True
    assert get_dependents("Y", vault_dir=vault_dir) == []


def test_remove_dependency_returns_false_when_missing(vault_dir):
    assert remove_dependency("X", "Y", vault_dir=vault_dir) is False


def test_remove_all_for_key_as_target(vault_dir):
    add_dependency("A", "BASE", vault_dir=vault_dir)
    add_dependency("B", "BASE", vault_dir=vault_dir)
    remove_all_for_key("BASE", vault_dir=vault_dir)
    assert get_dependents("BASE", vault_dir=vault_dir) == []


def test_remove_all_for_key_as_dependent(vault_dir):
    add_dependency("CHILD", "P1", vault_dir=vault_dir)
    add_dependency("CHILD", "P2", vault_dir=vault_dir)
    remove_all_for_key("CHILD", vault_dir=vault_dir)
    assert get_dependents("P1", vault_dir=vault_dir) == []
    assert get_dependents("P2", vault_dir=vault_dir) == []


def test_self_dependency_raises(vault_dir):
    with pytest.raises(ValueError, match="cannot depend on itself"):
        add_dependency("KEY", "KEY", vault_dir=vault_dir)
