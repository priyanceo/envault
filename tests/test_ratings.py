"""Tests for envault.ratings."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.storage import set_secret
from envault.ratings import (
    get_rating,
    list_by_rating,
    remove_rating,
    set_rating,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def _seed(vault_dir: Path, keys: list[str]) -> None:
    for k in keys:
        set_secret(k, f"val-{k}", PASSWORD, vault_dir=vault_dir)


def test_set_and_get_rating(vault_dir: Path) -> None:
    _seed(vault_dir, ["DB_URL"])
    set_rating("DB_URL", 4, PASSWORD, vault_dir=vault_dir)
    assert get_rating("DB_URL", vault_dir=vault_dir) == 4


def test_get_rating_returns_none_when_not_set(vault_dir: Path) -> None:
    _seed(vault_dir, ["API_KEY"])
    assert get_rating("API_KEY", vault_dir=vault_dir) is None


def test_set_rating_out_of_range_raises(vault_dir: Path) -> None:
    _seed(vault_dir, ["SECRET"])
    with pytest.raises(ValueError, match="between 1 and 5"):
        set_rating("SECRET", 6, PASSWORD, vault_dir=vault_dir)
    with pytest.raises(ValueError, match="between 1 and 5"):
        set_rating("SECRET", 0, PASSWORD, vault_dir=vault_dir)


def test_set_rating_missing_key_raises(vault_dir: Path) -> None:
    with pytest.raises(KeyError):
        set_rating("NONEXISTENT", 3, PASSWORD, vault_dir=vault_dir)


def test_set_rating_overwrites_existing(vault_dir: Path) -> None:
    _seed(vault_dir, ["TOKEN"])
    set_rating("TOKEN", 2, PASSWORD, vault_dir=vault_dir)
    set_rating("TOKEN", 5, PASSWORD, vault_dir=vault_dir)
    assert get_rating("TOKEN", vault_dir=vault_dir) == 5


def test_remove_rating_returns_true(vault_dir: Path) -> None:
    _seed(vault_dir, ["KEY"])
    set_rating("KEY", 3, PASSWORD, vault_dir=vault_dir)
    assert remove_rating("KEY", vault_dir=vault_dir) is True
    assert get_rating("KEY", vault_dir=vault_dir) is None


def test_remove_rating_returns_false_when_absent(vault_dir: Path) -> None:
    assert remove_rating("GHOST", vault_dir=vault_dir) is False


def test_list_by_rating_sorted_descending(vault_dir: Path) -> None:
    _seed(vault_dir, ["A", "B", "C"])
    set_rating("A", 2, PASSWORD, vault_dir=vault_dir)
    set_rating("B", 5, PASSWORD, vault_dir=vault_dir)
    set_rating("C", 3, PASSWORD, vault_dir=vault_dir)
    results = list_by_rating(vault_dir=vault_dir)
    assert results[0] == ("B", 5)
    assert results[1] == ("C", 3)
    assert results[2] == ("A", 2)


def test_list_by_rating_filtered(vault_dir: Path) -> None:
    _seed(vault_dir, ["X", "Y", "Z"])
    set_rating("X", 1, PASSWORD, vault_dir=vault_dir)
    set_rating("Y", 3, PASSWORD, vault_dir=vault_dir)
    set_rating("Z", 5, PASSWORD, vault_dir=vault_dir)
    results = list_by_rating(min_stars=3, max_stars=4, vault_dir=vault_dir)
    keys = [k for k, _ in results]
    assert "Y" in keys
    assert "X" not in keys
    assert "Z" not in keys


def test_list_by_rating_empty(vault_dir: Path) -> None:
    assert list_by_rating(vault_dir=vault_dir) == []
