"""CLI commands for managing secret priorities."""

import click
from pathlib import Path

from envault.priority import (
    set_priority,
    get_priority,
    remove_priority,
    list_by_priority,
    get_all_priorities,
    _VALID_PRIORITIES,
)


@click.group(name="priority")
def priority_cmd():
    """Manage priorities for secrets."""


@priority_cmd.command(name="set")
@click.argument("key")
@click.argument("priority", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def set_cmd(key, priority, vault_dir, password):
    """Set the priority of a secret KEY."""
    try:
        set_priority(Path(vault_dir), password, key, priority)
        click.echo(f"Priority for '{key}' set to '{priority}'.")
    except KeyError:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@priority_cmd.command(name="get")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def get_cmd(key, vault_dir):
    """Get the priority of a secret KEY."""
    result = get_priority(Path(vault_dir), key)
    if result is None:
        click.echo(f"No priority set for '{key}'.")
    else:
        click.echo(result)


@priority_cmd.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def remove_cmd(key, vault_dir):
    """Remove the priority of a secret KEY."""
    removed = remove_priority(Path(vault_dir), key)
    if removed:
        click.echo(f"Priority for '{key}' removed.")
    else:
        click.echo(f"No priority was set for '{key}'.")


@priority_cmd.command(name="list")
@click.option("--filter", "priority_filter", type=click.Choice(["low", "medium", "high", "critical"]), default=None)
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--sort", "sort_by_priority", is_flag=True, default=False, help="Sort output by priority level (critical first).")
def list_cmd(priority_filter, vault_dir, sort_by_priority):
    """List keys and their priorities."""
    _PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    if priority_filter:
        keys = list_by_priority(Path(vault_dir), priority_filter)
        if not keys:
            click.echo(f"No keys with priority '{priority_filter}'.")
        else:
            for k in keys:
                click.echo(f"{k}")
    else:
        all_p = get_all_priorities(Path(vault_dir))
        if not all_p:
            click.echo("No priorities set.")
        else:
            items = all_p.items()
            if sort_by_priority:
                items = sorted(items, key=lambda kv: _PRIORITY_ORDER.get(kv[1], 99))
            for k, v in items:
                click.echo(f"{k}: {v}")
