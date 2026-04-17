"""CLI commands for profile management."""
import click
from envault.profile import (
    list_profiles,
    get_profile_secrets,
    set_profile_secret,
    get_profile_secret,
    delete_profile_secret,
    delete_profile,
)


@click.group("profile")
def profile_cmd():
    """Manage named profiles (dev, staging, prod, …)."""


@profile_cmd.command("list")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def list_cmd(vault_dir, password):
    """List all profiles."""
    profiles = list_profiles(vault_dir, password)
    if not profiles:
        click.echo("No profiles found.")
    for p in profiles:
        click.echo(p)


@profile_cmd.command("set")
@click.argument("profile")
@click.argument("key")
@click.argument("value")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def set_cmd(profile, key, value, vault_dir, password):
    """Set KEY=VALUE in PROFILE."""
    set_profile_secret(vault_dir, password, profile, key, value)
    click.echo(f"Set {key} in profile '{profile}'.")


@profile_cmd.command("get")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def get_cmd(profile, key, vault_dir, password):
    """Get a secret from PROFILE."""
    value = get_profile_secret(vault_dir, password, profile, key)
    if value is None:
        click.echo(f"Key '{key}' not found in profile '{profile}'.", err=True)
        raise SystemExit(1)
    click.echo(value)


@profile_cmd.command("delete")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def delete_cmd(profile, key, vault_dir, password):
    """Delete KEY from PROFILE."""
    removed = delete_profile_secret(vault_dir, password, profile, key)
    if not removed:
        click.echo(f"Key '{key}' not found in profile '{profile}'.", err=True)
        raise SystemExit(1)
    click.echo(f"Deleted {key} from profile '{profile}'.")


@profile_cmd.command("drop")
@click.argument("profile")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def drop_cmd(profile, vault_dir, password):
    """Remove an entire PROFILE."""
    removed = delete_profile(vault_dir, password, profile)
    if not removed:
        click.echo(f"Profile '{profile}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Profile '{profile}' deleted.")
