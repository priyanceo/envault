"""Tests for profile management."""
import pytest
from click.testing import CliRunner
from envault.cli_profile import profile_cmd
from envault.profile import (
    list_profiles,
    get_profile_secrets,
    set_profile_secret,
    get_profile_secret,
    delete_profile_secret,
    delete_profile,
)


PASSWORD = "test-pass"


@pytest.fixture
def vault_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, vault_dir, args):
    return runner.invoke(
        profile_cmd,
        args,
        env={"ENVAULT_DIR": vault_dir, "ENVAULT_PASSWORD": PASSWORD},
    )


def test_set_and_get_secret(vault_dir):
    set_profile_secret(vault_dir, PASSWORD, "dev", "DB_URL", "postgres://localhost")
    assert get_profile_secret(vault_dir, PASSWORD, "dev", "DB_URL") == "postgres://localhost"


def test_list_profiles(vault_dir):
    set_profile_secret(vault_dir, PASSWORD, "dev", "K", "V")
    set_profile_secret(vault_dir, PASSWORD, "prod", "K", "V2")
    profiles = list_profiles(vault_dir, PASSWORD)
    assert set(profiles) == {"dev", "prod"}


def test_get_missing_key_returns_none(vault_dir):
    assert get_profile_secret(vault_dir, PASSWORD, "dev", "MISSING") is None


def test_delete_profile_secret(vault_dir):
    set_profile_secret(vault_dir, PASSWORD, "dev", "KEY", "val")
    removed = delete_profile_secret(vault_dir, PASSWORD, "dev", "KEY")
    assert removed is True
    assert get_profile_secret(vault_dir, PASSWORD, "dev", "KEY") is None


def test_delete_nonexistent_key(vault_dir):
    assert delete_profile_secret(vault_dir, PASSWORD, "dev", "NOPE") is False


def test_delete_profile_removes_all(vault_dir):
    set_profile_secret(vault_dir, PASSWORD, "staging", "A", "1")
    assert delete_profile(vault_dir, PASSWORD, "staging") is True
    assert list_profiles(vault_dir, PASSWORD) == []


def test_cli_set_and_get(runner, vault_dir):
    result = invoke(runner, vault_dir, ["set", "dev", "TOKEN", "abc123"])
    assert result.exit_code == 0
    result = invoke(runner, vault_dir, ["get", "dev", "TOKEN"])
    assert result.exit_code == 0
    assert "abc123" in result.output


def test_cli_get_missing_exits_nonzero(runner, vault_dir):
    result = invoke(runner, vault_dir, ["get", "dev", "GHOST"])
    assert result.exit_code != 0


def test_cli_list(runner, vault_dir):
    invoke(runner, vault_dir, ["set", "dev", "X", "1"])
    invoke(runner, vault_dir, ["set", "prod", "X", "2"])
    result = invoke(runner, vault_dir, ["list"])
    assert "dev" in result.output
    assert "prod" in result.output


def test_cli_drop(runner, vault_dir):
    invoke(runner, vault_dir, ["set", "dev", "X", "1"])
    result = invoke(runner, vault_dir, ["drop", "dev"])
    assert result.exit_code == 0
    result = invoke(runner, vault_dir, ["list"])
    assert "dev" not in result.output
