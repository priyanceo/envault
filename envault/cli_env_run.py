"""cli_env_run.py — CLI command to run a process with injected vault secrets."""

import sys
import click

from envault.env_run import run_with_secrets
from envault.storage import get_vault_path


@click.command("run", context_settings={"ignore_unknown_options": True})
@click.option("--password", "-p", envvar="ENVAULT_PASSWORD", required=True,
              help="Master password for the vault.")
@click.option("--profile", default=None, show_default=True,
              help="Restrict injected secrets to a specific profile.")
@click.option("--key", "-k", "keys", multiple=True,
              help="Inject only these specific keys (repeatable).")
@click.option("--vault-dir", default=None, envvar="ENVAULT_DIR",
              help="Override the vault directory.")
@click.argument("command", nargs=-1, type=click.UNPROCESSED, required=True)
def run_cmd(password, profile, keys, vault_dir, command):
    """Run COMMAND with vault secrets injected as environment variables.

    Example:

        envault run --password secret -- python manage.py runserver
    """
    resolved_dir = vault_dir or get_vault_path()
    selected_keys = list(keys) if keys else None

    try:
        exit_code = run_with_secrets(
            vault_dir=resolved_dir,
            password=password,
            command=list(command),
            profile=profile or None,
            keys=selected_keys,
        )
    except KeyError as exc:
        click.echo(f"Error: secret not found — {exc}", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    sys.exit(exit_code)
