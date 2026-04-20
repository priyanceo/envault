"""CLI commands for diffing vault secrets against a .env file."""

import click
from envault.diff import diff_vault_vs_file, format_diff
from envault.storage import get_vault_path


@click.group("diff")
def diff_cmd():
    """Compare vault secrets with a .env file."""


@diff_cmd.command("show")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--password", "-p", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--profile", default="default", show_default=True, help="Vault profile to compare.")
@click.option("--values", is_flag=True, default=False, help="Show values for changed keys.")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def show_cmd(filepath, password, profile, values, vault_dir):
    """Show differences between vault secrets and a .env file."""
    vdir = vault_dir or get_vault_path()
    try:
        entries = diff_vault_vs_file(vdir, password, filepath, profile=profile)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if not entries:
        click.echo("(no keys found)")
        return

    summary = {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}
    for e in entries:
        summary[e.status] += 1

    click.echo(format_diff(entries, show_values=values))
    click.echo(
        f"\nSummary: {summary['added']} added, {summary['removed']} removed, "
        f"{summary['changed']} changed, {summary['unchanged']} unchanged."
    )

    has_diff = any(e.status != "unchanged" for e in entries)
    if has_diff:
        raise SystemExit(1)
