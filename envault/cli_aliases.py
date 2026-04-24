"""CLI commands for managing secret key aliases."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from envault.aliases import (
    get_alias,
    list_aliases,
    remove_alias,
    set_alias,
)


@click.group("alias")
def alias_cmd() -> None:
    """Manage key aliases."""


@alias_cmd.command("set")
@click.argument("alias")
@click.argument("key")
@click.option("--vault-dir", default=None, type=click.Path(), help="Custom vault directory.")
def set_cmd(alias: str, key: str, vault_dir: Optional[str]) -> None:
    """Create or update ALIAS to point to KEY."""
    vd = Path(vault_dir) if vault_dir else None
    try:
        set_alias(alias, key, vault_dir=vd)
        click.echo(f"Alias '{alias}' -> '{key}' saved.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_cmd.command("get")
@click.argument("alias")
@click.option("--vault-dir", default=None, type=click.Path(), help="Custom vault directory.")
def get_cmd(alias: str, vault_dir: Optional[str]) -> None:
    """Show the key that ALIAS points to."""
    vd = Path(vault_dir) if vault_dir else None
    key = get_alias(alias, vault_dir=vd)
    if key is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(key)


@alias_cmd.command("remove")
@click.argument("alias")
@click.option("--vault-dir", default=None, type=click.Path(), help="Custom vault directory.")
def remove_cmd(alias: str, vault_dir: Optional[str]) -> None:
    """Remove an alias."""
    vd = Path(vault_dir) if vault_dir else None
    removed = remove_alias(alias, vault_dir=vd)
    if not removed:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Alias '{alias}' removed.")


@alias_cmd.command("list")
@click.option("--vault-dir", default=None, type=click.Path(), help="Custom vault directory.")
def list_cmd(vault_dir: Optional[str]) -> None:
    """List all aliases."""
    vd = Path(vault_dir) if vault_dir else None
    aliases = list_aliases(vault_dir=vd)
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        click.echo(f"{alias} -> {key}")
