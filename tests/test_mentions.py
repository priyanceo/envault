"""Tests for envault.mentions."""

from __future__ import annotations

import pytest

from envault.mentions import (
    extract_mentions,
    get_mentions,
    get_reverse_mentions,
    list_all_mentions,
    remove_mentions,
    update_mentions,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


# ---------------------------------------------------------------------------
# extract_mentions
# ---------------------------------------------------------------------------

def test_extract_mentions_curly_syntax():
    refs = extract_mentions("https://${API_HOST}:${PORT}/path")
    assert refs == ["API_HOST", "PORT"]


def test_extract_mentions_bare_dollar():
    refs = extract_mentions("prefix_$SECRET_KEY")
    assert "SECRET_KEY" in refs


def test_extract_mentions_no_refs():
    assert extract_mentions("plain value") == []


def test_extract_mentions_deduplicates():
    refs = extract_mentions("${FOO} and ${FOO}")
    assert refs.count("FOO") == 1


# ---------------------------------------------------------------------------
# update_mentions / get_mentions
# ---------------------------------------------------------------------------

def test_update_and_get_mentions(vault_dir):
    update_mentions(vault_dir, "DB_URL", "postgres://${DB_USER}:${DB_PASS}@host")
    refs = get_mentions(vault_dir, "DB_URL")
    assert "DB_USER" in refs
    assert "DB_PASS" in refs


def test_update_removes_stale_entry(vault_dir):
    update_mentions(vault_dir, "KEY", "${FOO}")
    update_mentions(vault_dir, "KEY", "no references here")
    assert get_mentions(vault_dir, "KEY") == []


def test_get_mentions_missing_key_returns_empty(vault_dir):
    assert get_mentions(vault_dir, "NONEXISTENT") == []


# ---------------------------------------------------------------------------
# get_reverse_mentions
# ---------------------------------------------------------------------------

def test_get_reverse_mentions(vault_dir):
    update_mentions(vault_dir, "A", "${SHARED}")
    update_mentions(vault_dir, "B", "${SHARED} and ${OTHER}")
    sources = get_reverse_mentions(vault_dir, "SHARED")
    assert "A" in sources
    assert "B" in sources


def test_get_reverse_mentions_empty_when_none(vault_dir):
    assert get_reverse_mentions(vault_dir, "ORPHAN") == []


# ---------------------------------------------------------------------------
# remove_mentions
# ---------------------------------------------------------------------------

def test_remove_mentions_returns_true(vault_dir):
    update_mentions(vault_dir, "X", "${Y}")
    assert remove_mentions(vault_dir, "X") is True
    assert get_mentions(vault_dir, "X") == []


def test_remove_mentions_missing_returns_false(vault_dir):
    assert remove_mentions(vault_dir, "GHOST") is False


# ---------------------------------------------------------------------------
# list_all_mentions
# ---------------------------------------------------------------------------

def test_list_all_mentions(vault_dir):
    update_mentions(vault_dir, "A", "${B}")
    update_mentions(vault_dir, "C", "${D}")
    data = list_all_mentions(vault_dir)
    assert "A" in data
    assert "C" in data


def test_list_all_mentions_empty_when_no_file(vault_dir):
    assert list_all_mentions(vault_dir) == {}
