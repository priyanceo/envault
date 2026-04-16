"""CLI command for rotating the vault password."""

import click
from envault.rotate import rotate_password


@click.command("rotate")
@click.option("--vault-dir", default=None, hidden=True)
def rotate_cmd(vault_dir):
    """Re-encrypt the vault with a new password."""
    old_password = click.prompt("Current password", hide_input=True)
    new_password = click.prompt(
        "New password", hide_input=True, confirmation_prompt=True
    )

    if old_password == new_password:
        click.echo("New password must differ from the current password.", err=True)
        raise SystemExit(1)

    try:
        count = rotate_password(
            vault_dir=vault_dir,
            old_password=old_password,
            new_password=new_password,
        )
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Rotation failed: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"Password rotated successfully. {count} secret(s) re-encrypted.")
