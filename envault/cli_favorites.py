"""CLI commands for managing favorite secrets in the vault."""

import click
from envault.favorites import add_favorite, remove_favorite, list_favorites, is_favorite


@click.group(name="favorites")
def favorites_cmd():
    """Manage favorite secrets."""


@favorites_cmd.command(name="add")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None, hidden=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def add_cmd(key, vault_dir, password):
    """Mark a secret KEY as a favorite."""
    try:
        add_favorite(key, password=password, vault_dir=vault_dir)
        click.echo(f"Added '{key}' to favorites.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@favorites_cmd.command(name="remove")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None, hidden=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def remove_cmd(key, vault_dir, password):
    """Remove a secret KEY from favorites."""
    removed = remove_favorite(key, password=password, vault_dir=vault_dir)
    if removed:
        click.echo(f"Removed '{key}' from favorites.")
    else:
        click.echo(f"'{key}' was not in favorites.", err=True)
        raise SystemExit(1)


@favorites_cmd.command(name="list")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None, hidden=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def list_cmd(vault_dir, password):
    """List all favorite secrets."""
    keys = list_favorites(password=password, vault_dir=vault_dir)
    if not keys:
        click.echo("No favorites saved.")
    else:
        for key in keys:
            click.echo(key)


@favorites_cmd.command(name="check")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None, hidden=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def check_cmd(key, vault_dir, password):
    """Check whether a secret KEY is marked as a favorite."""
    if is_favorite(key, password=password, vault_dir=vault_dir):
        click.echo(f"'{key}' is a favorite.")
    else:
        click.echo(f"'{key}' is not a favorite.")
        raise SystemExit(1)


def register(cli):
    """Register the favorites command group with the root CLI."""
    cli.add_command(favorites_cmd)
