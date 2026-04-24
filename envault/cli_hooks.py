"""CLI commands for managing pre/post operation hooks."""

import click
from envault.hooks import (
    VALID_EVENTS,
    register_hook,
    unregister_hook,
    get_hooks,
    list_hooks,
)


@click.group("hooks")
def hooks_cmd():
    """Manage pre/post operation hooks."""


@hooks_cmd.command("register")
@click.argument("event", type=click.Choice(VALID_EVENTS))
@click.argument("command")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def register_cmd(event, command, vault_dir):
    """Register a shell COMMAND to run on EVENT."""
    try:
        register_hook(event, command, vault_dir=vault_dir)
        click.echo(f"Hook registered: [{event}] -> {command}")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@hooks_cmd.command("unregister")
@click.argument("event", type=click.Choice(VALID_EVENTS))
@click.argument("command")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def unregister_cmd(event, command, vault_dir):
    """Unregister a hook COMMAND from EVENT."""
    removed = unregister_hook(event, command, vault_dir=vault_dir)
    if removed:
        click.echo(f"Hook removed: [{event}] -> {command}")
    else:
        click.echo(f"Hook not found for event '{event}'.", err=True)
        raise SystemExit(1)


@hooks_cmd.command("list")
@click.option("--event", type=click.Choice(VALID_EVENTS), default=None, help="Filter by event.")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def list_cmd(event, vault_dir):
    """List all registered hooks."""
    if event:
        cmds = get_hooks(event, vault_dir=vault_dir)
        if not cmds:
            click.echo(f"No hooks registered for '{event}'.")
        else:
            for cmd in cmds:
                click.echo(f"  [{event}] {cmd}")
    else:
        all_hooks = list_hooks(vault_dir=vault_dir)
        if not all_hooks:
            click.echo("No hooks registered.")
        else:
            for ev, cmds in sorted(all_hooks.items()):
                for cmd in cmds:
                    click.echo(f"  [{ev}] {cmd}")
