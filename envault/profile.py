"""Profile support: named sets of secrets (e.g. dev, staging, prod)."""
from envault.storage import load_vault, save_vault


DEFAULT_PROFILE = "default"


def list_profiles(vault_dir: str, password: str) -> list[str]:
    """Return all profile names present in the vault."""
    data = load_vault(vault_dir, password)
    return list(data.get("profiles", {}).keys())


def get_profile_secrets(vault_dir: str, password: str, profile: str) -> dict[str, str]:
    """Return all key/value pairs for a given profile."""
    data = load_vault(vault_dir, password)
    return dict(data.get("profiles", {}).get(profile, {}))


def set_profile_secret(vault_dir: str, password: str, profile: str, key: str, value: str) -> None:
    """Set a secret under a specific profile."""
    data = load_vault(vault_dir, password)
    data.setdefault("profiles", {}).setdefault(profile, {})[key] = value
    save_vault(vault_dir, password, data)


def get_profile_secret(vault_dir: str, password: str, profile: str, key: str) -> str | None:
    """Get a single secret from a profile."""
    return get_profile_secrets(vault_dir, password, profile).get(key)


def delete_profile_secret(vault_dir: str, password: str, profile: str, key: str) -> bool:
    """Delete a key from a profile. Returns True if key existed."""
    data = load_vault(vault_dir, password)
    profiles = data.get("profiles", {})
    if profile in profiles and key in profiles[profile]:
        del profiles[profile][key]
        if not profiles[profile]:
            del profiles[profile]
        save_vault(vault_dir, password, data)
        return True
    return False


def delete_profile(vault_dir: str, password: str, profile: str) -> bool:
    """Delete an entire profile. Returns True if it existed."""
    data = load_vault(vault_dir, password)
    if profile in data.get("profiles", {}):
        del data["profiles"][profile]
        save_vault(vault_dir, password, data)
        return True
    return False
