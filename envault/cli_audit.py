"""CLI commands for viewing the audit log."""

import os
from pathlib import Path

import click

from envault.audit import read_events, clear_audit_log, get_audit_path


@click.command("audit")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, help="Vault directory.")
@click.option("--clear", is_flag=True, default=False, help="Clear the audit log.")
@click.option("--tail", default=0, type=int, help="Show last N entries.")
def audit_cmd(vault_dir, clear, tail):
    """View or manage the audit log."""
    vdir = Path(vault_dir) if vault_dir else None

    if clear:
        clear_audit_log(vault_dir=vdir)
        click.echo("Audit log cleared.")
        return

    events = read_events(vault_dir=vdir)
    if not events:
        click.echo("No audit events found.")
        return

    if tail > 0:
        events = events[-tail:]

    for event in events:
        key_part = f"  key={event['key']}" if "key" in event else ""
        click.echo(f"{event['timestamp']}  {event['action']}{key_part}")
