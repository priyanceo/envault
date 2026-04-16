"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
SAMPLE_ENV = "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123"


def test_encrypt_returns_string():
    result = encrypt(SAMPLE_ENV, PASSWORD)
    assert isinstance(result, str)
    assert len(result) > 0


def test_encrypt_decrypt_roundtrip():
    token = encrypt(SAMPLE_ENV, PASSWORD)
    recovered = decrypt(token, PASSWORD)
    assert recovered == SAMPLE_ENV


def test_encrypt_produces_different_ciphertexts():
    """Each encryption should produce a unique output due to random salt/nonce."""
    token1 = encrypt(SAMPLE_ENV, PASSWORD)
    token2 = encrypt(SAMPLE_ENV, PASSWORD)
    assert token1 != token2


def test_decrypt_wrong_password_raises():
    token = encrypt(SAMPLE_ENV, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-password")


def test_decrypt_corrupted_payload_raises():
    token = encrypt(SAMPLE_ENV, PASSWORD)
    corrupted = token[:-4] + "AAAA"
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSWORD)


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid encoded payload"):
        decrypt("not!!valid==base64!!", PASSWORD)


def test_decrypt_too_short_payload_raises():
    import base64
    short = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="Payload too short"):
        decrypt(short, PASSWORD)


def test_encrypt_empty_string():
    token = encrypt("", PASSWORD)
    recovered = decrypt(token, PASSWORD)
    assert recovered == ""
