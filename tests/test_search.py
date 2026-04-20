"""Tests for envault search functionality."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.storage import set_secret
from envault.tags import add_tag
from envault.profile import set_profile_secret
from envault.search import search_by_pattern, search_by_tag
from envault.cli_search import search_cmd

PASSWORD = "hunter2"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


def _seed(vault_dir):
    set_secret(vault_dir, PASSWORD, "DB_HOST", "localhost")
    set_secret(vault_dir, PASSWORD, "DB_PORT", "5432")
    set_secret(vault_dir, PASSWORD, "API_KEY", "abc123")
    add_tag(vault_dir, "DB_HOST", "database")
    add_tag(vault_dir, "DB_PORT", "database")
    set_profile_secret(vault_dir, PASSWORD, "prod", "DB_HOST", "prod-db")


def test_search_by_exact_pattern(vault_dir):
    _seed(vault_dir)
    results = search_by_pattern(vault_dir, PASSWORD, "DB_HOST")
    keys = [(r.source, r.key) for r in results]
    assert ("default", "DB_HOST") in keys
    assert ("prod", "DB_HOST") in keys


def test_search_by_glob_pattern(vault_dir):
    _seed(vault_dir)
    results = search_by_pattern(vault_dir, PASSWORD, "DB_*")
    keys = [r.key for r in results]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "API_KEY" not in keys


def test_search_no_profiles(vault_dir):
    _seed(vault_dir)
    results = search_by_pattern(vault_dir, PASSWORD, "DB_HOST", include_profiles=False)
    sources = [r.source for r in results]
    assert "prod" not in sources
    assert "default" in sources


def test_search_by_tag(vault_dir):
    _seed(vault_dir)
    results = search_by_tag(vault_dir, PASSWORD, "database")
    keys = [r.key for r in results]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "API_KEY" not in keys


def test_search_by_tag_no_match(vault_dir):
    _seed(vault_dir)
    results = search_by_tag(vault_dir, PASSWORD, "nonexistent")
    assert results == []


def test_search_result_includes_tags(vault_dir):
    _seed(vault_dir)
    results = search_by_pattern(vault_dir, PASSWORD, "DB_HOST", include_profiles=False)
    default_result = next(r for r in results if r.source == "default")
    assert "database" in default_result.tags


def invoke(runner, vault_dir, *args):
    env = {"ENVAULT_VAULT_DIR": vault_dir, "ENVAULT_PASSWORD": PASSWORD}
    return runner.invoke(search_cmd, list(args), env=env)


def test_cli_pattern_command(vault_dir, runner):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, "pattern", "DB_*")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "DB_PORT" in result.output


def test_cli_tag_command(vault_dir, runner):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, "tag", "database")
    assert result.exit_code == 0
    assert "DB_HOST" in result.output


def test_cli_pattern_no_match(vault_dir, runner):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, "pattern", "MISSING_*")
    assert result.exit_code == 0
    assert "No secrets matched" in result.output
