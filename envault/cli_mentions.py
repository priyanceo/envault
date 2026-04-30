"""CLI commands for the mentions feature."""

from __future__ import annotations

import click

from envault.mentions import (
    get_mentions,
    get_reverse_mentions,
    list_all_mentions,
    remove_mentions,
)


@click.group(name="mentions")
def mentions_cmd():
    """Inspect cross-references between secrets."""


@mentions_cmd.command(name="get")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def get_cmd(key: str, vault_dir: str):
    """Show keys that KEY references."""
    refs = get_mentions(vault_dir, key)
    if not refs:
        click.echo(f"{key} references no other keys.")
    else:
        click.echo(f"{key} references: {', '.join(refs)}")


@mentions_cmd.command(name="reverse")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def reverse_cmd(key: str, vault_dir: str):
    """Show keys that reference KEY."""
    sources = get_reverse_mentions(vault_dir, key)
    if not sources:
        click.echo(f"No keys reference {key}.")
    else:
        click.echo(f"Keys referencing {key}: {', '.join(sources)}")


@mentions_cmd.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def remove_cmd(key: str, vault_dir: str):
    """Remove mention records for KEY."""
    removed = remove_mentions(vault_dir, key)
    if removed:
        click.echo(f"Removed mention records for {key}.")
    else:
        click.echo(f"No mention records found for {key}.")


@mentions_cmd.command(name="list")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
def list_cmd(vault_dir: str):
    """List all mention relationships."""
    data = list_all_mentions(vault_dir)
    if not data:
        click.echo("No mentions recorded.")
        return
    for src, refs in sorted(data.items()):
        click.echo(f"{src} -> {', '.join(refs)}")


def register(cli: click.Group) -> None:
    cli.add_command(mentions_cmd)
