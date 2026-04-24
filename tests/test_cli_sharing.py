"""CLI tests for envault share commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import patch
from envault.cli_sharing import share_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_dir(tmp_path):
    return str(tmp_path)


def invoke(runner, vault_dir, args, input_text=None):
    return runner.invoke(
        share_cmd,
        ["--vault-dir", vault_dir] + args if "--vault-dir" in str(args) else args,
        input=input_text,
        catch_exceptions=False,
    )


def test_create_and_redeem_single_secret(runner, vault_dir):
    with patch("envault.sharing.get_secret", return_value="supersecret"):
        result = runner.invoke(
            share_cmd,
            ["create", "API_KEY", "--vault-dir", vault_dir,
             "--password", "vaultpw", "--share-password", "sharepw"],
            catch_exceptions=False,
        )
    assert result.exit_code == 0
    assert "Share token for 'API_KEY'" in result.output
    token_line = [l for l in result.output.splitlines() if l and "Share token" not in l]
    token = token_line[0].strip()

    result2 = runner.invoke(
        share_cmd,
        ["redeem", token, "--share-password", "sharepw"],
        catch_exceptions=False,
    )
    assert result2.exit_code == 0
    assert "API_KEY=supersecret" in result2.output


def test_create_missing_key_exits_nonzero(runner, vault_dir):
    with patch("envault.sharing.get_secret", return_value=None):
        result = runner.invoke(
            share_cmd,
            ["create", "MISSING", "--vault-dir", vault_dir,
             "--password", "pw", "--share-password", "sp"],
        )
    assert result.exit_code != 0


def test_redeem_wrong_password_exits_nonzero(runner, vault_dir):
    with patch("envault.sharing.get_secret", return_value="v"):
        r = runner.invoke(
            share_cmd,
            ["create", "K", "--vault-dir", vault_dir,
             "--password", "vp", "--share-password", "sp"],
            catch_exceptions=False,
        )
    token = [l for l in r.output.splitlines() if l and "Share token" not in l][0].strip()
    result = runner.invoke(share_cmd, ["redeem", token, "--share-password", "wrong"])
    assert result.exit_code != 0


def test_bundle_and_redeem(runner, vault_dir):
    secrets = {"A": "1", "B": "2"}
    with patch("envault.sharing.get_secret", side_effect=lambda d, p, k: secrets.get(k)):
        r = runner.invoke(
            share_cmd,
            ["bundle", "A", "B", "--vault-dir", vault_dir,
             "--password", "vp", "--share-password", "sp"],
            catch_exceptions=False,
        )
    assert r.exit_code == 0
    token = [l for l in r.output.splitlines() if l and "Bundle token" not in l][0].strip()

    r2 = runner.invoke(share_cmd, ["redeem-bundle", token, "--share-password", "sp"],
                       catch_exceptions=False)
    assert r2.exit_code == 0
    assert "A=1" in r2.output
    assert "B=2" in r2.output
