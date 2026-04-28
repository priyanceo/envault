"""CLI commands for managing key expiry dates."""

from __future__ import annotations

from datetime import datetime, timezone

import click

from envault.expiry import (
    get_expiry,
    is_expired,
    list_expiring,
    remove_expiry,
    set_expiry,
)


@click.group("expiry")
def expiry_cmd():
    """Manage key expiry dates."""


@expiry_cmd.command("set")
@click.argument("key")
@click.argument("expires_at")  # ISO 8601, e.g. 2025-12-31T00:00:00
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def set_cmd(key: str, expires_at: str, vault_dir: str, password: str):
    """Set an expiry date for KEY (ISO 8601 format)."""
    try:
        dt = datetime.fromisoformat(expires_at).replace(tzinfo=timezone.utc)
    except ValueError:
        raise click.ClickException(f"Invalid datetime format: {expires_at!r}")
    try:
        set_expiry(vault_dir, password, key, dt)
    except KeyError:
        raise click.ClickException(f"Key not found: {key!r}")
    click.echo(f"Expiry set for '{key}': {dt.isoformat()}")


@expiry_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def get_cmd(key: str, vault_dir: str):
    """Show the expiry date for KEY."""
    expiry = get_expiry(vault_dir, key)
    if expiry is None:
        click.echo(f"No expiry set for '{key}'.")
    else:
        expired = is_expired(vault_dir, key)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"{key}: {expiry.isoformat()}{status}")


@expiry_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove the expiry date for KEY."""
    removed = remove_expiry(vault_dir, key)
    if removed:
        click.echo(f"Expiry removed for '{key}'.")
    else:
        click.echo(f"No expiry was set for '{key}'.")


@expiry_cmd.command("list")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def list_cmd(vault_dir: str):
    """List all keys with expiry dates, sorted by expiry."""
    entries = list_expiring(vault_dir)
    if not entries:
        click.echo("No expiry dates set.")
        return
    now = datetime.now(timezone.utc)
    for key, expiry in entries:
        expired = now >= expiry
        flag = " [EXPIRED]" if expired else ""
        click.echo(f"{key}: {expiry.isoformat()}{flag}")


def register(main_cli):
    main_cli.add_command(expiry_cmd)
