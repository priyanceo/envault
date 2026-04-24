"""Tests for envault.sharing — share token creation and redemption."""

import pytest
import os
from unittest.mock import patch
from envault.sharing import (
    create_share_token, redeem_share_token,
    create_bundle, redeem_bundle,
)


SHARE_PW = "share-secret-pw"
VAULT_PW = "vault-pw"
KEY = "MY_API_KEY"
VALUE = "abc123"


@pytest.fixture()
def mock_get_secret():
    with patch("envault.sharing.get_secret") as m:
        m.return_value = VALUE
        yield m


def test_create_and_redeem_share_token(mock_get_secret, tmp_path):
    token = create_share_token(str(tmp_path), VAULT_PW, KEY, SHARE_PW)
    assert isinstance(token, str)
    assert len(token) > 20
    result = redeem_share_token(token, SHARE_PW)
    assert result["key"] == KEY
    assert result["value"] == VALUE


def test_share_token_wrong_password_raises(mock_get_secret, tmp_path):
    token = create_share_token(str(tmp_path), VAULT_PW, KEY, SHARE_PW)
    with pytest.raises(ValueError, match="Failed to redeem"):
        redeem_share_token(token, "wrong-password")


def test_share_token_missing_key_raises(tmp_path):
    with patch("envault.sharing.get_secret", return_value=None):
        with pytest.raises(KeyError, match="MY_API_KEY"):
            create_share_token(str(tmp_path), VAULT_PW, KEY, SHARE_PW)


def test_create_and_redeem_bundle(tmp_path):
    secrets = {"KEY1": "val1", "KEY2": "val2", "KEY3": "val3"}
    with patch("envault.sharing.get_secret", side_effect=lambda d, p, k: secrets.get(k)):
        token = create_bundle(str(tmp_path), VAULT_PW, list(secrets.keys()), SHARE_PW)
        result = redeem_bundle(token, SHARE_PW)
    assert result == secrets


def test_bundle_missing_key_raises(tmp_path):
    with patch("envault.sharing.get_secret", return_value=None):
        with pytest.raises(KeyError, match="MISSING"):
            create_bundle(str(tmp_path), VAULT_PW, ["MISSING"], SHARE_PW)


def test_bundle_wrong_password_raises(tmp_path):
    with patch("envault.sharing.get_secret", return_value="v"):
        token = create_bundle(str(tmp_path), VAULT_PW, ["K"], SHARE_PW)
    with pytest.raises(ValueError, match="Failed to redeem bundle"):
        redeem_bundle(token, "bad-pw")


def test_redeem_corrupted_token_raises():
    with pytest.raises(ValueError):
        redeem_share_token("notavalidtoken!!", SHARE_PW)


def test_tokens_are_different_each_call(mock_get_secret, tmp_path):
    t1 = create_share_token(str(tmp_path), VAULT_PW, KEY, SHARE_PW)
    t2 = create_share_token(str(tmp_path), VAULT_PW, KEY, SHARE_PW)
    assert t1 != t2
