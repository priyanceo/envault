"""Tests for envault.cascade and envault.cli_cascade."""

from __future__ import annotations

import os
import pytest
from click.testing import CliRunner

from envault.storage import set_secret
from envault.profile import set_profile_secret
from envault.cascade import resolve, resolve_all, MAX_DEPTH
from envault.cli_cascade import cascade_cmd

PASSWORD = "hunter2"


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        cascade_cmd,
        ["--vault-dir", vault_dir, "--password", PASSWORD, *args],
        catch_exceptions=False,
    )


def _seed(vault_dir):
    set_secret(vault_dir, "ROOT_KEY", "root_value", PASSWORD)
    set_secret(vault_dir, "SHARED", "from_root", PASSWORD)
    set_profile_secret(vault_dir, "dev", "DEV_KEY", "dev_value", PASSWORD)
    set_profile_secret(vault_dir, "dev", "SHARED", "from_dev", PASSWORD)
    set_profile_secret(vault_dir, "staging", "STAGING_KEY", "staging_value", PASSWORD)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_resolve_finds_profile_value(vault_dir):
    _seed(vault_dir)
    value, source = resolve("DEV_KEY", PASSWORD, vault_dir, ["dev"])
    assert value == "dev_value"
    assert source == "dev"


def test_resolve_falls_back_to_root(vault_dir):
    _seed(vault_dir)
    value, source = resolve("ROOT_KEY", PASSWORD, vault_dir, ["dev"])
    assert value == "root_value"
    assert source == "__root__"


def test_resolve_profile_shadows_root(vault_dir):
    _seed(vault_dir)
    value, source = resolve("SHARED", PASSWORD, vault_dir, ["dev"])
    assert value == "from_dev"
    assert source == "dev"


def test_resolve_returns_none_when_missing(vault_dir):
    _seed(vault_dir)
    value, source = resolve("MISSING", PASSWORD, vault_dir, ["dev"])
    assert value is None
    assert source is None


def test_resolve_raises_on_deep_chain(vault_dir):
    chain = [f"p{i}" for i in range(MAX_DEPTH + 1)]
    with pytest.raises(ValueError, match="MAX_DEPTH"):
        resolve("KEY", PASSWORD, vault_dir, chain)


def test_resolve_all_merges_correctly(vault_dir):
    _seed(vault_dir)
    merged = resolve_all(PASSWORD, vault_dir, ["dev"])
    assert merged["SHARED"] == ("from_dev", "dev")
    assert merged["ROOT_KEY"] == ("root_value", "__root__")
    assert merged["DEV_KEY"] == ("dev_value", "dev")


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_get_from_profile(vault_dir, runner):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, "get", "DEV_KEY", "-p", "dev")
    assert result.exit_code == 0
    assert "dev_value" in result.output


def test_cli_get_missing_exits_nonzero(vault_dir, runner):
    _seed(vault_dir)
    result = runner.invoke(
        cascade_cmd,
        ["get", "NOPE", "-p", "dev", "--vault-dir", vault_dir, "--password", PASSWORD],
    )
    assert result.exit_code != 0


def test_cli_resolve_all_shows_source(vault_dir, runner):
    _seed(vault_dir)
    result = invoke(runner, vault_dir, "resolve-all", "-p", "dev", "--show-source")
    assert result.exit_code == 0
    assert "from_dev" in result.output
    assert "__root__" in result.output
