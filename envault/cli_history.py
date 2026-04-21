"""CLI commands for secret history management."""

import click
from datetime import datetime

from envault.history import get_history, clear_history, list_keys_with_history


@click.group("history")
def history_cmd():
    """View and manage secret value history."""


@history_cmd.command("show")
@click.argument("key")
@click.option("--vault-dir", default=None, hidden=True)
def show_cmd(key, vault_dir):
    """Show the value history for a secret KEY."""
    entries = get_history(key, vault_dir=vault_dir)
    if not entries:
        click.echo(f"No history found for '{key}'.")
        raise SystemExit(1)
    click.echo(f"History for '{key}' ({len(entries)} entries):")
    for i, entry in enumerate(entries, 1):
        ts = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"  [{i}] {ts}  {entry['value']}")


@history_cmd.command("clear")
@click.argument("key")
@click.option("--vault-dir", default=None, hidden=True)
def clear_cmd(key, vault_dir):
    """Clear all history for a secret KEY."""
    removed = clear_history(key, vault_dir=vault_dir)
    if removed:
        click.echo(f"History cleared for '{key}'.")
    else:
        click.echo(f"No history found for '{key}'.")
        raise SystemExit(1)


@history_cmd.command("list")
@click.option("--vault-dir", default=None, hidden=True)
def list_cmd(vault_dir):
    """List all keys that have recorded history."""
    keys = list_keys_with_history(vault_dir=vault_dir)
    if not keys:
        click.echo("No history recorded yet.")
    else:
        for k in sorted(keys):
            click.echo(k)
