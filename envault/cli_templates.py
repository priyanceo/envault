"""CLI commands for template management."""
from __future__ import annotations

import click

from envault.storage import get_vault_path, list_secrets
from envault.templates import (
    check_template,
    delete_template,
    get_template,
    list_templates,
    save_template,
)


@click.group("template")
def template_cmd() -> None:
    """Manage key templates."""


@template_cmd.command("save")
@click.argument("name")
@click.argument("keys", nargs=-1, required=True)
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None)
def save_cmd(name: str, keys: tuple, vault_dir: str | None) -> None:
    """Save a named template with the given KEYS."""
    vd = get_vault_path(vault_dir)
    save_template(vd, name, list(keys))
    click.echo(f"Template '{name}' saved with {len(keys)} key(s).")


@template_cmd.command("list")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None)
def list_cmd(vault_dir: str | None) -> None:
    """List all saved templates."""
    vd = get_vault_path(vault_dir)
    names = list_templates(vd)
    if not names:
        click.echo("No templates found.")
        return
    for n in names:
        click.echo(n)


@template_cmd.command("show")
@click.argument("name")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None)
def show_cmd(name: str, vault_dir: str | None) -> None:
    """Show keys in a template."""
    vd = get_vault_path(vault_dir)
    keys = get_template(vd, name)
    if keys is None:
        click.echo(f"Template '{name}' not found.", err=True)
        raise SystemExit(1)
    for k in keys:
        click.echo(k)


@template_cmd.command("delete")
@click.argument("name")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None)
def delete_cmd(name: str, vault_dir: str | None) -> None:
    """Delete a template."""
    vd = get_vault_path(vault_dir)
    if not delete_template(vd, name):
        click.echo(f"Template '{name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Template '{name}' deleted.")


@template_cmd.command("check")
@click.argument("name")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--profile", default="default", show_default=True)
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", default=None)
def check_cmd(name: str, password: str, profile: str, vault_dir: str | None) -> None:
    """Check vault keys against a template, reporting missing/extra keys."""
    vd = get_vault_path(vault_dir)
    try:
        present = list_secrets(vd, password, profile)
    except Exception as exc:
        click.echo(f"Error reading vault: {exc}", err=True)
        raise SystemExit(1)
    try:
        result = check_template(vd, name, present)
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    if result["missing"]:
        click.echo("Missing keys:")
        for k in result["missing"]:
            click.echo(f"  - {k}")
    if result["extra"]:
        click.echo("Extra keys (not in template):")
        for k in result["extra"]:
            click.echo(f"  + {k}")
    if not result["missing"] and not result["extra"]:
        click.echo("All keys match the template.")
