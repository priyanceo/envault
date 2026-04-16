"""Password rotation: re-encrypt vault with a new password."""

from envault.storage import load_vault, save_vault, get_vault_path


def rotate_password(vault_dir: str, old_password: str, new_password: str) -> int:
    """Re-encrypt all secrets with a new password.

    Returns the number of secrets that were rotated.
    """
    vault = load_vault(old_password, vault_dir=vault_dir)
    secrets = vault.get("secrets", {})
    save_vault(vault, new_password, vault_dir=vault_dir)
    return len(secrets)
