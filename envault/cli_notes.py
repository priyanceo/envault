"""CLI commands for managing per-secret notes."""

import click

from envault.notes import set_note, get_note, remove_note, list_notes


@click.group("notes")
def notes_cmd():
    """Manage notes/annotations attached to secrets."""


@notes_cmd.command("set")
@click.argument("key")
@click.argument("note")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def set_cmd(key: str, note: str, vault_dir: str, password: str):
    """Attach NOTE to the secret KEY."""
    try:
        set_note(vault_dir, password, key, note)
        click.echo(f"Note set for '{key}'.")
    except KeyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@notes_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def get_cmd(key: str, vault_dir: str, password: str):
    """Show the note attached to KEY."""
    note = get_note(vault_dir, password, key)
    if note is None:
        click.echo(f"No note found for '{key}'.", err=True)
        raise SystemExit(1)
    click.echo(note)


@notes_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def remove_cmd(key: str, vault_dir: str, password: str):
    """Remove the note attached to KEY."""
    removed = remove_note(vault_dir, password, key)
    if removed:
        click.echo(f"Note removed for '{key}'.")
    else:
        click.echo(f"No note to remove for '{key}'.")


@notes_cmd.command("list")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", required=True)
def list_cmd(vault_dir: str, password: str):
    """List all keys that have notes."""
    all_notes = list_notes(vault_dir, password)
    if not all_notes:
        click.echo("No notes found.")
        return
    for key, note in sorted(all_notes.items()):
        click.echo(f"{key}: {note}")
