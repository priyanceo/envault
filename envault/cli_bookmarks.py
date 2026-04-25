"""CLI commands for managing bookmarks."""

from __future__ import annotations

import click

from envault.bookmarks import (
    add_bookmark,
    remove_bookmark,
    list_bookmarks,
    is_bookmarked,
    clear_bookmarks,
)


@click.group("bookmarks")
def bookmarks_cmd() -> None:
    """Manage bookmarked secrets for quick access."""


@bookmarks_cmd.command("add")
@click.argument("key")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def add_cmd(key: str, password: str, vault_dir: str | None) -> None:
    """Bookmark a secret KEY."""
    try:
        added = add_bookmark(key, password, vault_dir=vault_dir)
    except KeyError:
        click.echo(f"Error: key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    if added:
        click.echo(f"Bookmarked '{key}'.")
    else:
        click.echo(f"'{key}' is already bookmarked.")


@bookmarks_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def remove_cmd(key: str, vault_dir: str | None) -> None:
    """Remove KEY from bookmarks."""
    removed = remove_bookmark(key, vault_dir=vault_dir)
    if removed:
        click.echo(f"Removed bookmark '{key}'.")
    else:
        click.echo(f"'{key}' was not bookmarked.", err=True)
        raise SystemExit(1)


@bookmarks_cmd.command("list")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def list_cmd(vault_dir: str | None) -> None:
    """List all bookmarked keys."""
    keys = list_bookmarks(vault_dir=vault_dir)
    if not keys:
        click.echo("No bookmarks set.")
    else:
        for k in keys:
            click.echo(k)


@bookmarks_cmd.command("check")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def check_cmd(key: str, vault_dir: str | None) -> None:
    """Check whether KEY is bookmarked."""
    if is_bookmarked(key, vault_dir=vault_dir):
        click.echo(f"'{key}' is bookmarked.")
    else:
        click.echo(f"'{key}' is not bookmarked.")
        raise SystemExit(1)


@bookmarks_cmd.command("clear")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def clear_cmd(vault_dir: str | None) -> None:
    """Remove all bookmarks."""
    count = clear_bookmarks(vault_dir=vault_dir)
    click.echo(f"Cleared {count} bookmark(s).")
