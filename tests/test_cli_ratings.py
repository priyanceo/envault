"""CLI tests for envault ratings commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_ratings import ratings_cmd
from envault.storage import set_secret

PASSWORD = "test-password"


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path


def invoke(runner: CliRunner, vault_dir: Path, args: list[str], password: str = PASSWORD):
    full_args = []
    for arg in args:
        full_args.append(arg)
    # inject --vault-dir and --password where applicable
    extra = ["--vault-dir", str(vault_dir)]
    return runner.invoke(ratings_cmd, full_args + extra, input=password + "\n")


def _seed(vault_dir: Path, key: str) -> None:
    set_secret(key, f"val-{key}", PASSWORD, vault_dir=vault_dir)


def test_set_and_get_rating(runner: CliRunner, vault_dir: Path) -> None:
    _seed(vault_dir, "DB_URL")
    result = runner.invoke(
        ratings_cmd,
        ["set", "DB_URL", "4", "--password", PASSWORD, "--vault-dir", str(vault_dir)],
    )
    assert result.exit_code == 0
    assert "4 star" in result.output

    result2 = runner.invoke(
        ratings_cmd, ["get", "DB_URL", "--vault-dir", str(vault_dir)]
    )
    assert result2.exit_code == 0
    assert "4/5" in result2.output


def test_get_missing_rating_exits_nonzero(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        ratings_cmd, ["get", "NOPE", "--vault-dir", str(vault_dir)]
    )
    assert result.exit_code != 0


def test_set_invalid_stars_exits_nonzero(runner: CliRunner, vault_dir: Path) -> None:
    _seed(vault_dir, "KEY")
    result = runner.invoke(
        ratings_cmd,
        ["set", "KEY", "9", "--password", PASSWORD, "--vault-dir", str(vault_dir)],
    )
    assert result.exit_code != 0


def test_remove_rating(runner: CliRunner, vault_dir: Path) -> None:
    _seed(vault_dir, "TOKEN")
    runner.invoke(
        ratings_cmd,
        ["set", "TOKEN", "3", "--password", PASSWORD, "--vault-dir", str(vault_dir)],
    )
    result = runner.invoke(
        ratings_cmd, ["remove", "TOKEN", "--vault-dir", str(vault_dir)]
    )
    assert result.exit_code == 0
    assert "removed" in result.output.lower()


def test_list_ratings(runner: CliRunner, vault_dir: Path) -> None:
    for k, s in [("A", 5), ("B", 2)]:
        _seed(vault_dir, k)
        runner.invoke(
            ratings_cmd,
            ["set", k, str(s), "--password", PASSWORD, "--vault-dir", str(vault_dir)],
        )
    result = runner.invoke(
        ratings_cmd, ["list", "--vault-dir", str(vault_dir)]
    )
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" in result.output
    # A (5 stars) should appear before B (2 stars)
    assert result.output.index("A") < result.output.index("B")


def test_list_empty(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        ratings_cmd, ["list", "--vault-dir", str(vault_dir)]
    )
    assert result.exit_code == 0
    assert "No ratings" in result.output
