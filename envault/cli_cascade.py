"""CLI commands for cascade resolution across profile chains."""

from __future__ import annotations

import click

from envault.cascade import resolve, resolve_all


@click.group("cascade")
def cascade_cmd() -> None:
    """Resolve secrets by walking a profile inheritance chain."""


@cascade_cmd.command("get")
@click.argument("key")
@click.option("--profile", "-p", multiple=True, help="Profile(s) in priority order.")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def get_cmd(
    key: str,
    profile: tuple[str, ...],
    vault_dir: str,
    password: str,
) -> None:
    """Resolve KEY walking PROFILE chain, falling back to the root vault."""
    value, source = resolve(key, password, vault_dir, list(profile))
    if value is None:
        click.echo(f"Key '{key}' not found in chain.", err=True)
        raise SystemExit(1)
    click.echo(f"{value}  # from: {source}")


@cascade_cmd.command("resolve-all")
@click.option("--profile", "-p", multiple=True, help="Profile(s) in priority order.")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--show-source", is_flag=True, default=False, help="Show which profile each key came from.")
def resolve_all_cmd(
    profile: tuple[str, ...],
    vault_dir: str,
    password: str,
    show_source: bool,
) -> None:
    """Print all resolved keys for the given profile chain."""
    merged = resolve_all(password, vault_dir, list(profile))
    if not merged:
        click.echo("No secrets found.")
        return
    for key, (value, source) in sorted(merged.items()):
        if show_source:
            click.echo(f"{key}={value}  # {source}")
        else:
            click.echo(f"{key}={value}")


def register(parent: click.Group) -> None:
    parent.add_command(cascade_cmd)
