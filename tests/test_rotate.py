"""Tests for password rotation."""

import pytest
from click.testing import CliRunner

from envault.storage import set_secret, get_secret
from envault.rotate import rotate_password
from envault.cli_rotate import rotate_cmd


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def test_rotate_reencrypts_secrets(vault_dir):
    set_secret("KEY", "value", "old", vault_dir=vault_dir)
    set_secret("KEY2", "value2", "old", vault_dir=vault_dir)

    count = rotate_password(vault_dir, "old", "new")

    assert count == 2
    assert get_secret("KEY", "new", vault_dir=vault_dir) == "value"
    assert get_secret("KEY2", "new", vault_dir=vault_dir) == "value2"


def test_rotate_old_password_no_longer_works(vault_dir):
    set_secret("X", "y", "old", vault_dir=vault_dir)
    rotate_password(vault_dir, "old", "new")

    with pytest.raises(Exception):
        get_secret("X", "old", vault_dir=vault_dir)


def test_rotate_empty_vault(vault_dir):
    count = rotate_password(vault_dir, "old", "new")
    assert count == 0


def _runner():
    return CliRunner(mix_stderr=False)


def invoke(vault_dir, inputs):
    runner = _runner()
    return runner.invoke(
        rotate_cmd,
        ["--vault-dir", vault_dir],
        input="\n".join(inputs) + "\n",
        catch_exceptions=False,
    )


def test_cli_rotate_success(vault_dir):
    set_secret("A", "1", "old", vault_dir=vault_dir)
    result = invoke(vault_dir, ["old", "new", "new"])
    assert result.exit_code == 0
    assert "1 secret(s) re-encrypted" in result.output


def test_cli_rotate_same_password_exits_nonzero(vault_dir):
    runner = _runner()
    result = runner.invoke(
        rotate_cmd,
        ["--vault-dir", vault_dir],
        input="same\nsame\nsame\n",
    )
    assert result.exit_code != 0


def test_cli_rotate_wrong_old_password_exits_nonzero(vault_dir):
    set_secret("A", "1", "correct", vault_dir=vault_dir)
    result = invoke(vault_dir, ["wrong", "new", "new"])
    assert result.exit_code != 0
