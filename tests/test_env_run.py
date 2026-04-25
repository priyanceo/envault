"""Tests for envault.env_run and the `run` CLI command."""

import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envault.storage import set_secret, get_vault_path
from envault.env_run import build_env, run_with_secrets
from envault.cli_env_run import run_cmd


@pytest.fixture()
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    monkeypatch.setattr("envault.env_run.get_secret",
                        lambda d, p, k: _fake_secrets(d, p).get(k))
    monkeypatch.setattr("envault.env_run.list_secrets",
                        lambda d, p: list(_fake_secrets(d, p).keys()))
    return str(tmp_path)


def _fake_secrets(_dir, _pwd):
    return {"APP_KEY": "abc123", "DB_URL": "sqlite:///db"}


def _seed(tmp_path, password="pass"):
    """Actually write secrets using real storage for integration tests."""
    set_secret(str(tmp_path), password, "APP_KEY", "abc123")
    set_secret(str(tmp_path), password, "DB_URL", "sqlite:///db")


# ---------------------------------------------------------------------------
# Unit tests for build_env
# ---------------------------------------------------------------------------

def test_build_env_injects_all_secrets(vault_dir):
    env = build_env(vault_dir, "pass")
    assert env["APP_KEY"] == "abc123"
    assert env["DB_URL"] == "sqlite:///db"


def test_build_env_inherits_os_environ(vault_dir, monkeypatch):
    monkeypatch.setenv("EXISTING_VAR", "present")
    env = build_env(vault_dir, "pass")
    assert env["EXISTING_VAR"] == "present"


def test_build_env_filters_by_keys(vault_dir):
    env = build_env(vault_dir, "pass", keys=["APP_KEY"])
    assert "APP_KEY" in env
    assert "DB_URL" not in env


def test_build_env_extra_env_takes_priority(vault_dir):
    env = build_env(vault_dir, "pass", extra_env={"APP_KEY": "override"})
    assert env["APP_KEY"] == "override"


# ---------------------------------------------------------------------------
# Integration test for run_with_secrets
# ---------------------------------------------------------------------------

def test_run_with_secrets_exit_code(vault_dir):
    with patch("envault.env_run.subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        code = run_with_secrets(vault_dir, "pass", ["echo", "hi"])
    assert code == 0
    called_env = mock_run.call_args.kwargs["env"]
    assert called_env["APP_KEY"] == "abc123"


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

def test_cli_run_passes_secrets_to_command(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    runner = CliRunner()

    with patch("envault.cli_env_run.run_with_secrets") as mock_run:
        mock_run.return_value = 0
        result = runner.invoke(
            run_cmd,
            ["--password", "pass", "--", "env"],
            catch_exceptions=False,
        )

    assert result.exit_code == 0
    mock_run.assert_called_once()


def test_cli_run_propagates_nonzero_exit(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    runner = CliRunner()

    with patch("envault.cli_env_run.run_with_secrets", return_value=42):
        result = runner.invoke(run_cmd, ["--password", "pass", "--", "false"])

    assert result.exit_code == 42
