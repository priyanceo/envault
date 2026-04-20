"""CLI commands for managing per-key access control."""

from __future__ import annotations

import click

from envault.access import (
    check_permission,
    get_permissions,
    list_acl,
    remove_permissions,
    set_permissions,
)


@click.group("access")
def access_cmd():
    """Manage per-key read/write permissions."""


@access_cmd.command("set")
@click.argument("key")
@click.option("--perms", required=True, help="Comma-separated permissions: read,write")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def set_cmd(ctx, key, perms, password):
    """Set permissions for KEY (e.g. --perms read or --perms read,write)."""
    vault_dir = ctx.obj.get("vault_dir") if ctx.obj else None
    perm_set = {p.strip() for p in perms.split(",") if p.strip()}
    try:
        set_permissions(key, perm_set, password, vault_dir=vault_dir)
        click.echo(f"Permissions for '{key}' set to: {', '.join(sorted(perm_set))}")
    except (KeyError, ValueError) as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@access_cmd.command("get")
@click.argument("key")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def get_cmd(ctx, key, password):
    """Show current permissions for KEY."""
    vault_dir = ctx.obj.get("vault_dir") if ctx.obj else None
    perms = get_permissions(key, password, vault_dir=vault_dir)
    click.echo(f"{key}: {', '.join(sorted(perms)) if perms else '(none)'}")


@access_cmd.command("remove")
@click.argument("key")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def remove_cmd(ctx, key, password):
    """Remove explicit ACL entry for KEY (reverts to default: all permissions)."""
    vault_dir = ctx.obj.get("vault_dir") if ctx.obj else None
    remove_permissions(key, password, vault_dir=vault_dir)
    click.echo(f"ACL entry for '{key}' removed (defaults restored).")


@access_cmd.command("check")
@click.argument("key")
@click.argument("permission")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def check_cmd(ctx, key, permission, password):
    """Check if PERMISSION is granted for KEY. Exits 0 if allowed, 1 if denied."""
    vault_dir = ctx.obj.get("vault_dir") if ctx.obj else None
    allowed = check_permission(key, permission, password, vault_dir=vault_dir)
    if allowed:
        click.echo(f"'{permission}' is ALLOWED for '{key}'.")
    else:
        click.echo(f"'{permission}' is DENIED for '{key}'.")
        ctx.exit(1)


@access_cmd.command("list")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.pass_context
def list_cmd(ctx, password):
    """List all explicit ACL entries in the vault."""
    vault_dir = ctx.obj.get("vault_dir") if ctx.obj else None
    acl = list_acl(password, vault_dir=vault_dir)
    if not acl:
        click.echo("No explicit ACL entries found.")
        return
    for key, perms in sorted(acl.items()):
        click.echo(f"  {key}: {', '.join(perms)}")
