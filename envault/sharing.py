"""Sharing: generate and verify shareable encrypted bundles for secrets."""

import json
import base64
import secrets
from typing import Optional
from envault.crypto import encrypt, decrypt
from envault.storage import get_secret, vault_file


def create_share_token(vault_dir: str, password: str, key: str, share_password: str) -> str:
    """Create a shareable token for a single secret, re-encrypted with share_password."""
    value = get_secret(vault_dir, password, key)
    if value is None:
        raise KeyError(f"Secret '{key}' not found in vault.")
    payload = json.dumps({"key": key, "value": value})
    encrypted = encrypt(payload, share_password)
    token_bytes = base64.urlsafe_b64encode(encrypted.encode()).decode()
    return token_bytes


def redeem_share_token(token: str, share_password: str) -> dict:
    """Decode and decrypt a share token, returning {key, value}."""
    try:
        encrypted = base64.urlsafe_b64decode(token.encode()).decode()
        payload = decrypt(encrypted, share_password)
        return json.loads(payload)
    except Exception as exc:
        raise ValueError(f"Failed to redeem share token: {exc}") from exc


def create_bundle(vault_dir: str, password: str, keys: list, share_password: str) -> str:
    """Bundle multiple secrets into a single shareable encrypted token."""
    bundle = {}
    for key in keys:
        value = get_secret(vault_dir, password, key)
        if value is None:
            raise KeyError(f"Secret '{key}' not found in vault.")
        bundle[key] = value
    payload = json.dumps(bundle)
    encrypted = encrypt(payload, share_password)
    token_bytes = base64.urlsafe_b64encode(encrypted.encode()).decode()
    return token_bytes


def redeem_bundle(token: str, share_password: str) -> dict:
    """Decode and decrypt a bundle token, returning dict of {key: value}."""
    try:
        encrypted = base64.urlsafe_b64decode(token.encode()).decode()
        payload = decrypt(encrypted, share_password)
        return json.loads(payload)
    except Exception as exc:
        raise ValueError(f"Failed to redeem bundle: {exc}") from exc
