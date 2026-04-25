"""CLI commands for label management."""

from __future__ import annotations

import click

from envault.labels import set_label, get_labels, remove_label, clear_labels, find_by_label


@click.group("labels")
def labels_cmd():
    """Manage key/value labels on secrets."""


@labels_cmd.command("set")
@click.argument("key")
@click.argument("label_key")
@click.argument("label_value")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def set_cmd(key, label_key, label_value, password, vault_dir):
    """Attach LABEL_KEY=LABEL_VALUE to secret KEY."""
    try:
        set_label(key, label_key, label_value, password, vault_dir=vault_dir)
        click.echo(f"Label '{label_key}' set on '{key}'.")
    except KeyError:
        click.echo(f"Error: secret '{key}' not found.", err=True)
        raise SystemExit(1)


@labels_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def get_cmd(key, vault_dir):
    """List all labels for secret KEY."""
    labels = get_labels(key, vault_dir=vault_dir)
    if not labels:
        click.echo(f"No labels for '{key}'.")
    else:
        for lk, lv in sorted(labels.items()):
            click.echo(f"  {lk}={lv}")


@labels_cmd.command("remove")
@click.argument("key")
@click.argument("label_key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def remove_cmd(key, label_key, vault_dir):
    """Remove LABEL_KEY from secret KEY."""
    removed = remove_label(key, label_key, vault_dir=vault_dir)
    if removed:
        click.echo(f"Label '{label_key}' removed from '{key}'.")
    else:
        click.echo(f"Label '{label_key}' not found on '{key}'.", err=True)
        raise SystemExit(1)


@labels_cmd.command("clear")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def clear_cmd(key, vault_dir):
    """Remove all labels from secret KEY."""
    clear_labels(key, vault_dir=vault_dir)
    click.echo(f"All labels cleared from '{key}'.")


@labels_cmd.command("find")
@click.argument("label_key")
@click.argument("label_value", required=False, default=None)
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
def find_cmd(label_key, label_value, vault_dir):
    """Find secrets that have LABEL_KEY (optionally matching LABEL_VALUE)."""
    results = find_by_label(label_key, label_value, vault_dir=vault_dir)
    if not results:
        click.echo("No matching secrets.")
    else:
        for secret_key, labels in sorted(results.items()):
            pairs = ", ".join(f"{k}={v}" for k, v in sorted(labels.items()))
            click.echo(f"  {secret_key}: {pairs}")
