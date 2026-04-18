"""CLI commands for vault snapshots."""
import click
from pathlib import Path
from envault.snapshot import create_snapshot, list_snapshots, restore_snapshot, delete_snapshot
from envault.storage import get_vault_path


@click.group("snapshot")
def snapshot_cmd():
    """Manage vault snapshots."""


@snapshot_cmd.command("create")
@click.option("--vault-dir", default=None, hidden=True)
@click.option("--label", default="", help="Optional label for the snapshot.")
@click.password_option(prompt="Vault password")
def create_cmd(vault_dir, label, password):
    """Create a snapshot of the current vault."""
    vd = Path(vault_dir) if vault_dir else get_vault_path().parent
    try:
        path = create_snapshot(vd, password, label)
        click.echo(f"Snapshot created: {path.name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@snapshot_cmd.command("list")
@click.option("--vault-dir", default=None, hidden=True)
def list_cmd(vault_dir):
    """List available snapshots."""
    vd = Path(vault_dir) if vault_dir else get_vault_path().parent
    snaps = list_snapshots(vd)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for s in snaps:
        label = f" [{s['label']}]" if s["label"] else ""
        click.echo(f"{s['file']}{label}  ({s['count']} secrets)")


@snapshot_cmd.command("restore")
@click.argument("filename")
@click.option("--vault-dir", default=None, hidden=True)
@click.password_option(prompt="Vault password")
def restore_cmd(filename, vault_dir, password):
    """Restore vault from a snapshot."""
    vd = Path(vault_dir) if vault_dir else get_vault_path().parent
    try:
        count = restore_snapshot(vd, password, filename)
        click.echo(f"Restored {count} secret(s) from {filename}.")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@snapshot_cmd.command("delete")
@click.argument("filename")
@click.option("--vault-dir", default=None, hidden=True)
def delete_cmd(filename, vault_dir):
    """Delete a snapshot."""
    vd = Path(vault_dir) if vault_dir else get_vault_path().parent
    try:
        delete_snapshot(vd, filename)
        click.echo(f"Deleted snapshot: {filename}")
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
