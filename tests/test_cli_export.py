"""Tests for import/export CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_export import import_cmd, export_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVAULT_DIR", str(tmp_path))
    return tmp_path


def invoke(runner, cmd, args, password="testpass"):
    return runner.invoke(cmd, args, input=f"{password}\n")


def test_import_from_file(runner, vault_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\nFOO=bar\n")
    result = invoke(runner, import_cmd, [str(env_file)])
    assert result.exit_code == 0
    assert "Imported 2 variable(s)" in result.output


def test_import_empty_file(runner, vault_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# just a comment\n")
    result = invoke(runner, import_cmd, [str(env_file)])
    assert result.exit_code == 0
    assert "No variables found" in result.output


def test_export_to_stdout(runner, vault_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    invoke(runner, import_cmd, [str(env_file)])
    result = invoke(runner, export_cmd, ["--stdout"])
    assert result.exit_code == 0
    assert "KEY=value" in result.output


def test_export_to_file(runner, vault_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=value\n")
    invoke(runner, import_cmd, [str(env_file)])
    out_file = tmp_path / "out.env"
    result = invoke(runner, export_cmd, [str(out_file)])
    assert result.exit_code == 0
    assert out_file.exists()
    assert "KEY=value" in out_file.read_text()


def test_export_empty_vault(runner, vault_dir):
    result = invoke(runner, export_cmd, ["--stdout"])
    assert result.exit_code == 0
    assert "No secrets found" in result.output


def test_import_export_roundtrip(runner, vault_dir, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\nB=2\nC=3\n")
    invoke(runner, import_cmd, [str(env_file)])
    out_file = tmp_path / "out.env"
    invoke(runner, export_cmd, [str(out_file)])
    content = out_file.read_text()
    assert "A=1" in content
    assert "B=2" in content
    assert "C=3" in content
