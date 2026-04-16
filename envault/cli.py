"""CLI entry point for envault."""

import click
from pathlib import Path

from envault.storage import (
    set_secret,
    get_secret,
    delete_secret,
    list_projects,
    load_vault,
    DEFAULT_VAULT_DIR,
)


@click.group()
@click.option("--vault-dir", default=None, help="Custom vault directory path.")
@click.pass_context
def cli(ctx: click.Context, vault_dir: str | None) -> None:
    """envault — securely manage .env secrets."""
    ctx.ensure_object(dict)
    ctx.obj["vault_dir"] = Path(vault_dir) if vault_dir else DEFAULT_VAULT_DIR


@cli.command()
@click.argument("project")
@click.argument("key")
@click.argument("value")
@click.password_option(prompt="Vault password")
@click.pass_context
def set(ctx: click.Context, project: str, key: str, value: str, password: str) -> None:
    """Set a secret KEY=VALUE for PROJECT."""
    set_secret(project, key, value, password, ctx.obj["vault_dir"])
    click.echo(f"✔ Set {project}/{key}")


@cli.command()
@click.argument("project")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_context
def get(ctx: click.Context, project: str, key: str, password: str) -> None:
    """Get a secret by PROJECT and KEY."""
    value = get_secret(project, key, password, ctx.obj["vault_dir"])
    if value is None:
        click.echo(f"Key '{key}' not found in project '{project}'.", err=True)
        raise SystemExit(1)
    click.echo(value)


@cli.command()
@click.argument("project")
@click.argument("key")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_context
def delete(ctx: click.Context, project: str, key: str, password: str) -> None:
    """Delete a secret from PROJECT by KEY."""
    removed = delete_secret(project, key, password, ctx.obj["vault_dir"])
    if removed:
        click.echo(f"✔ Deleted {project}/{key}")
    else:
        click.echo(f"Key '{key}' not found in project '{project}'.", err=True)
        raise SystemExit(1)


@cli.command(name="list")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_context
def list_cmd(ctx: click.Context, password: str) -> None:
    """List all projects in the vault."""
    projects = list_projects(password, ctx.obj["vault_dir"])
    if not projects:
        click.echo("No projects found.")
    for project in projects:
        click.echo(project)


if __name__ == "__main__":
    cli()
