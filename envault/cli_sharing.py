"""CLI commands for sharing secrets via encrypted tokens."""

import click
from envault.sharing import create_share_token, redeem_share_token, create_bundle, redeem_bundle


@click.group("share")
def share_cmd():
    """Share secrets securely via encrypted tokens."""


@share_cmd.command("create")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--share-password", prompt=True, hide_input=True, confirmation_prompt=True,
              help="Password to protect the share token.")
def create_cmd(key, vault_dir, password, share_password):
    """Create a shareable token for a single secret KEY."""
    try:
        token = create_share_token(vault_dir, password, key, share_password)
        click.echo(f"Share token for '{key}':\n{token}")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@share_cmd.command("redeem")
@click.argument("token")
@click.option("--share-password", prompt=True, hide_input=True,
              help="Password used when creating the token.")
def redeem_cmd(token, share_password):
    """Redeem a single-secret share TOKEN and print the key/value."""
    try:
        result = redeem_share_token(token, share_password)
        click.echo(f"{result['key']}={result['value']}")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@share_cmd.command("bundle")
@click.argument("keys", nargs=-1, required=True)
@click.option("--vault-dir", envvar="ENVAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--share-password", prompt=True, hide_input=True, confirmation_prompt=True)
def bundle_cmd(keys, vault_dir, password, share_password):
    """Bundle multiple KEYS into a single shareable encrypted token."""
    try:
        token = create_bundle(vault_dir, password, list(keys), share_password)
        click.echo(f"Bundle token:\n{token}")
    except KeyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@share_cmd.command("redeem-bundle")
@click.argument("token")
@click.option("--share-password", prompt=True, hide_input=True)
def redeem_bundle_cmd(token, share_password):
    """Redeem a bundle TOKEN and print all key=value pairs."""
    try:
        result = redeem_bundle(token, share_password)
        for k, v in result.items():
            click.echo(f"{k}={v}")
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
