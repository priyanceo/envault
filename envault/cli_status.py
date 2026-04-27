"""CLI command for displaying the aggregated status of a vault key."""

import click

from envault.status import get_key_status, format_status


@click.group("status")
def status_cmd():
    """Show aggregated status for vault keys."""


@status_cmd.command("show")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True, help="Vault directory")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def show_cmd(key: str, vault_dir: str, password: str):
    """Show status for KEY."""
    status = get_key_status(vault_dir, password, key)
    click.echo(format_status(status))


@status_cmd.command("check")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--assert-exists", is_flag=True, default=False, help="Exit non-zero if key missing")
@click.option("--assert-not-expired", is_flag=True, default=False, help="Exit non-zero if expired")
def check_cmd(key: str, vault_dir: str, password: str, assert_exists: bool, assert_not_expired: bool):
    """Check status conditions for KEY and exit non-zero on failure."""
    status = get_key_status(vault_dir, password, key)

    if assert_exists and not status.exists:
        raise click.ClickException(f"Key '{key}' does not exist in the vault.")

    if assert_not_expired and status.expired:
        raise click.ClickException(f"Key '{key}' has expired.")

    click.echo(format_status(status))


def register(main_cli):
    main_cli.add_command(status_cmd)
