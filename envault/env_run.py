"""env_run.py — Run a subprocess with secrets injected as environment variables."""

import os
import subprocess
from typing import Optional

from envault.storage import get_secret, list_secrets
from envault.audit import log_event


def build_env(
    vault_dir: str,
    password: str,
    profile: Optional[str] = None,
    keys: Optional[list] = None,
    extra_env: Optional[dict] = None,
) -> dict:
    """Build an environment dict by injecting vault secrets into os.environ.

    Args:
        vault_dir: Path to the vault directory.
        password: Master password for decryption.
        profile: Optional profile name to scope secrets.
        keys: Optional explicit list of keys to inject; defaults to all.
        extra_env: Optional additional variables to merge (highest priority).

    Returns:
        A copy of the current environment with secrets injected.
    """
    env = os.environ.copy()

    if profile:
        from envault.profile import get_profile_secrets
        secrets = get_profile_secrets(vault_dir, password, profile)
    else:
        all_keys = list_secrets(vault_dir, password)
        secrets = {k: get_secret(vault_dir, password, k) for k in all_keys}

    if keys is not None:
        secrets = {k: v for k, v in secrets.items() if k in keys}

    env.update(secrets)

    if extra_env:
        env.update(extra_env)

    return env


def run_with_secrets(
    vault_dir: str,
    password: str,
    command: list,
    profile: Optional[str] = None,
    keys: Optional[list] = None,
) -> int:
    """Run *command* with vault secrets injected into its environment.

    Returns:
        The process exit code.
    """
    env = build_env(vault_dir, password, profile=profile, keys=keys)
    log_event(vault_dir, "env_run", key=None, extra={"command": command[0]})
    result = subprocess.run(command, env=env)
    return result.returncode
