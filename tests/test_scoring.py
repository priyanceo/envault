"""Tests for envault.scoring."""

import os
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from click.testing import CliRunner

from envault.storage import set_secret, init_vault
from envault.expiry import set_expiry
from envault.scoring import score_key, score_all, SecretScore
from envault.cli_scoring import scoring_cmd

PASSWORD = "test-pass"


@pytest.fixture()
def vault_dir(tmp_path):
    d = str(tmp_path / "vault")
    os.makedirs(d, exist_ok=True)
    init_vault(d, PASSWORD)
    return d


@pytest.fixture()
def runner():
    return CliRunner()


def invoke(runner, vault_dir, *args):
    return runner.invoke(
        scoring_cmd,
        ["--vault-dir", vault_dir, "--password", PASSWORD, *args],
        catch_exceptions=False,
    )


def test_score_key_returns_none_for_missing(vault_dir):
    result = score_key("NO_SUCH_KEY", vault_dir, PASSWORD)
    assert result is None


def test_score_key_basic(vault_dir):
    set_secret(vault_dir, PASSWORD, "MY_KEY", "Str0ng!Secret#99")
    s = score_key("MY_KEY", vault_dir, PASSWORD)
    assert isinstance(s, SecretScore)
    assert s.key == "MY_KEY"
    assert 0 <= s.complexity_score <= 100
    assert 0 <= s.overall <= 100
    assert not s.has_expiry
    assert not s.is_expired
    assert any("expiry" in sug.lower() for sug in s.suggestions)


def test_score_key_with_expiry_boosts_score(vault_dir):
    set_secret(vault_dir, PASSWORD, "EXP_KEY", "Str0ng!Secret#99")
    future = datetime.now(timezone.utc) + timedelta(days=30)
    set_expiry(vault_dir, PASSWORD, "EXP_KEY", future)
    s = score_key("EXP_KEY", vault_dir, PASSWORD)
    assert s.has_expiry
    assert not s.is_expired


def test_score_key_expired_reduces_score(vault_dir):
    set_secret(vault_dir, PASSWORD, "OLD_KEY", "Str0ng!Secret#99")
    past = datetime.now(timezone.utc) - timedelta(days=1)
    set_expiry(vault_dir, PASSWORD, "OLD_KEY", past)
    s = score_key("OLD_KEY", vault_dir, PASSWORD)
    assert s.is_expired
    assert any("expired" in sug.lower() for sug in s.suggestions)


def test_score_all_returns_all_keys(vault_dir):
    set_secret(vault_dir, PASSWORD, "K1", "abc")
    set_secret(vault_dir, PASSWORD, "K2", "Str0ng!Secret#99")
    results = score_all(vault_dir, PASSWORD, ["K1", "K2"])
    assert set(results.keys()) == {"K1", "K2"}


def test_cli_show_existing_key(vault_dir, runner):
    set_secret(vault_dir, PASSWORD, "CLI_KEY", "Str0ng!Secret#99")
    result = invoke(runner, vault_dir, "show", "CLI_KEY")
    assert result.exit_code == 0
    assert "Overall score" in result.output


def test_cli_show_missing_key_exits_nonzero(vault_dir, runner):
    result = runner.invoke(
        scoring_cmd,
        ["show", "MISSING", "--vault-dir", vault_dir, "--password", PASSWORD],
    )
    assert result.exit_code != 0


def test_cli_audit_empty_vault(vault_dir, runner):
    result = invoke(runner, vault_dir, "audit")
    assert result.exit_code == 0
    assert "empty" in result.output.lower()
