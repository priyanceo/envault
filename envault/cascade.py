"""Cascade resolution: resolve a key's value by walking a profile inheritance chain."""

from __future__ import annotations

from typing import Optional

from envault.storage import get_secret
from envault.profile import get_profile_secret, list_profiles


MAX_DEPTH = 16


def resolve(
    key: str,
    password: str,
    vault_dir: str,
    profile_chain: list[str],
) -> tuple[Optional[str], Optional[str]]:
    """Walk *profile_chain* left-to-right and return the first hit.

    Returns ``(value, source)`` where *source* is the profile name that
    provided the value, or ``'__root__'`` if it came from the root vault.
    Returns ``(None, None)`` when the key cannot be found anywhere.

    Raises ``ValueError`` if the chain is longer than ``MAX_DEPTH``.
    """
    if len(profile_chain) > MAX_DEPTH:
        raise ValueError(
            f"Profile chain length {len(profile_chain)} exceeds MAX_DEPTH {MAX_DEPTH}"
        )

    for profile in profile_chain:
        value = get_profile_secret(vault_dir, profile, key, password)
        if value is not None:
            return value, profile

    # Fall back to root vault
    value = get_secret(vault_dir, key, password)
    if value is not None:
        return value, "__root__"

    return None, None


def resolve_all(
    password: str,
    vault_dir: str,
    profile_chain: list[str],
) -> dict[str, tuple[str, str]]:
    """Resolve every key visible from *profile_chain*.

    Returns a mapping of ``key -> (value, source)``.
    Keys from earlier profiles shadow later ones and the root vault.
    """
    from envault.storage import list_secrets
    from envault.profile import get_profile_secrets

    merged: dict[str, tuple[str, str]] = {}

    # Start from the root so that higher-priority profiles can override
    root_keys = list_secrets(vault_dir, password)
    for k, v in root_keys.items():
        merged[k] = (v, "__root__")

    # Walk chain in reverse so the first profile wins
    for profile in reversed(profile_chain):
        secrets = get_profile_secrets(vault_dir, profile, password)
        for k, v in secrets.items():
            merged[k] = (v, profile)

    return merged
