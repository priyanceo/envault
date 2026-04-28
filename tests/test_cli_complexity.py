"""Tests for envault.cli_complexity commands."""

import os
import pytest
from click.testing import CliRunner
from envault.cli_complexity import complexity_cmd
from envault.storage import set_secret


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def invoke(runner, vault_dir, args, password="testpass", **kwargs):
    env = {"ENVAULT_DIR": vault_dir}
    return runner.invoke(
        complexity_cmd,
        args,
        env=env,
        catch_exceptions=False,
        **kwargs,
    )


def test_check_strong_value_passes(runner):
    result = runner.invoke(complexity_cmd, ["check", "MyStr0ng!Pass99"])
    assert result.exit_code == 0
    assert "PASS" in result.output


def test_check_weak_value_fails(runner):
    result = runner.invoke(complexity_cmd, ["check", "abc"])
    assert result.exit_code != 0
    assert "FAIL" in result.output


def test_check_shows_score(runner):
    result = runner.invoke(complexity_cmd, ["check", "MyStr0ng!Pass"])
    assert "Score" in result.output
    assert "/4" in result.output


def test_check_shows_suggestions_for_weak(runner):
    result = runner.invoke(complexity_cmd, ["check", "alllowercase1"])
    assert "uppercase" in result.output.lower() or "special" in result.output.lower()


def test_audit_no_weak_secrets(runner, vault_dir):
    pw = "vaultpass"
    set_secret("API_KEY", "MyStr0ng!Pass99", pw, vault_dir=vault_dir)
    result = invoke(runner, vault_dir, ["audit", "--password", pw])
    assert result.exit_code == 0
    assert "meet the complexity" in result.output


def test_audit_detects_weak_secret(runner, vault_dir):
    pw = "vaultpass"
    set_secret("WEAK_KEY", "abc12345", pw, vault_dir=vault_dir)
    result = invoke(runner, vault_dir, ["audit", "--password", pw])
    assert result.exit_code != 0
    assert "WEAK_KEY" in result.output


def test_audit_specific_keys_only(runner, vault_dir):
    pw = "vaultpass"
    set_secret("STRONG", "MyStr0ng!Pass99", pw, vault_dir=vault_dir)
    set_secret("WEAK", "abc12345", pw, vault_dir=vault_dir)
    # audit only STRONG — should pass
    result = invoke(runner, vault_dir, ["audit", "--password", pw, "STRONG"])
    assert result.exit_code == 0
