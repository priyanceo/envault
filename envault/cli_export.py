"""CLI commands for importing and exporting .env files."""

import click
from pathlib import Path

from envault.storage import load_vault, save_vault, get_vault_path
from envault.export import import_dotenv_file, export_dotenv_file, render_dotenv


@click.command("import")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--project", default="default", show_default=True, help="Project name")
def import_cmd(file: str, password: str, project: str) -> None:
    """Import key-value pairs from a .env FILE into the vault."""
    pairs = import_dotenv_file(file)
    if not pairs:
        click.echo("No variables found in file.")
        return
    vault = load_vault(password, project)
    vault.update(pairs)
    save_vault(vault, password, project)
    click.echo(f"Imported {len(pairs)} variable(s) into project '{project}'.")


@click.command("export")
@click.argument("file", type=click.Path(dir_okay=False), required=False)
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--project", default="default", show_default=True, help="Project name")
@click.option("--stdout", "to_stdout", is_flag=True, help="Print to stdout instead of file")
def export_cmd(file: str | None, password: str, project: str, to_stdout: bool) -> None:
    """Export vault secrets for PROJECT to a .env FILE."""
    vault = load_vault(password, project)
    if not vault:
        click.echo(f"No secrets found for project '{project}'.")
        return
    if to_stdout or not file:
        click.echo(render_dotenv(vault), nl=False)
    else:
        export_dotenv_file(vault, file)
        click.echo(f"Exported {len(vault)} variable(s) to '{file}'.")
