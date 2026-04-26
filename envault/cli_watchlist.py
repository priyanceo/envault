"""CLI commands for managing the watchlist."""

from __future__ import annotations

import click

from envault.watchlist import (
    watch_key,
    unwatch_key,
    is_watched,
    get_watch_reason,
    list_watched,
    clear_watchlist,
)


@click.group("watchlist")
def watchlist_cmd():
    """Manage the key watchlist."""


@watchlist_cmd.command("watch")
@click.argument("key")
@click.option("--reason", default="", help="Reason for watching this key.")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def watch_cmd(key, reason, vault_dir):
    """Add KEY to the watchlist."""
    watch_key(key, reason=reason, vault_dir=vault_dir)
    click.echo(f"Watching '{key}'.")


@watchlist_cmd.command("unwatch")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def unwatch_cmd(key, vault_dir):
    """Remove KEY from the watchlist."""
    removed = unwatch_key(key, vault_dir=vault_dir)
    if removed:
        click.echo(f"No longer watching '{key}'.")
    else:
        click.echo(f"'{key}' was not on the watchlist.", err=True)
        raise SystemExit(1)


@watchlist_cmd.command("check")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def check_cmd(key, vault_dir):
    """Check if KEY is on the watchlist."""
    if is_watched(key, vault_dir=vault_dir):
        reason = get_watch_reason(key, vault_dir=vault_dir)
        msg = f"'{key}' is watched."
        if reason:
            msg += f" Reason: {reason}"
        click.echo(msg)
    else:
        click.echo(f"'{key}' is not watched.")
        raise SystemExit(1)


@watchlist_cmd.command("list")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def list_cmd(vault_dir):
    """List all watched keys."""
    entries = list_watched(vault_dir=vault_dir)
    if not entries:
        click.echo("No keys are being watched.")
        return
    for entry in entries:
        line = entry["key"]
        if entry["reason"]:
            line += f"  # {entry['reason']}"
        click.echo(line)


@watchlist_cmd.command("clear")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def clear_cmd(vault_dir):
    """Remove all keys from the watchlist."""
    count = clear_watchlist(vault_dir=vault_dir)
    click.echo(f"Cleared {count} key(s) from the watchlist.")
