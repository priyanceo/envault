"""Main CLI entry point for envault."""

from __future__ import annotations

import click

from envault.storage import delete_secret, get_secret, list_secrets, set_secret


@click.group()
@click.option(
    "--vault-dir",
    envvar="ENVAULT_VAULT_DIR",
    default=None,
    help="Override the vault directory.",
)
@click.pass_context
def cli(ctx, vault_dir):
    """envault — secure .env manager."""
    ctx.ensure_object(dict)
    ctx.obj["vault_dir"] = vault_dir


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def set(ctx, key, value, password):
    """Store a secret KEY=VALUE in the vault."""
    vault_dir = ctx.obj.get("vault_dir")
    set_secret(key, value, password, vault_dir=vault_dir)
    click.echo(f"Set '{key}'.")


@cli.command("get")
@click.argument("key")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def get(ctx, key, password):
    """Retrieve a secret by KEY."""
    vault_dir = ctx.obj.get("vault_dir")
    value = get_secret(key, password, vault_dir=vault_dir)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        ctx.exit(1)
    else:
        click.echo(value)


@cli.command("delete")
@click.argument("key")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def delete(ctx, key, password):
    """Delete a secret by KEY."""
    vault_dir = ctx.obj.get("vault_dir")
    delete_secret(key, password, vault_dir=vault_dir)
    click.echo(f"Deleted '{key}'.")


@cli.command("list")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def list_cmd(ctx, password):
    """List all secret keys in the vault."""
    vault_dir = ctx.obj.get("vault_dir")
    keys = list_secrets(password, vault_dir=vault_dir)
    if not keys:
        click.echo("No secrets stored.")
    else:
        for k in keys:
            click.echo(k)


# Register sub-command groups
from envault.cli_export import export_cmd, import_cmd  # noqa: E402
from envault.cli_rotate import rotate_cmd  # noqa: E402
from envault.cli_audit import audit_cmd  # noqa: E402
from envault.cli_profile import profile_cmd  # noqa: E402
from envault.cli_snapshot import snapshot_cmd  # noqa: E402
from envault.cli_diff import diff_cmd  # noqa: E402
from envault.cli_search import search_cmd  # noqa: E402
from envault.cli_access import access_cmd  # noqa: E402

cli.add_command(import_cmd, "import")
cli.add_command(export_cmd, "export")
cli.add_command(rotate_cmd, "rotate")
cli.add_command(audit_cmd, "audit")
cli.add_command(profile_cmd, "profile")
cli.add_command(snapshot_cmd, "snapshot")
cli.add_command(diff_cmd, "diff")
cli.add_command(search_cmd, "search")
cli.add_command(access_cmd, "access")
