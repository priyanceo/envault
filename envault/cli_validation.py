"""CLI commands for validating secret keys and values."""

from __future__ import annotations

import click

from envault.validation import validate_key, validate_value, validate_key_value


@click.group("validate")
def validation_cmd() -> None:
    """Validate keys and values before storing them."""


@validation_cmd.command("key")
@click.argument("key")
def key_cmd(key: str) -> None:
    """Check whether KEY is a valid secret key name."""
    result = validate_key(key)
    if result.valid:
        click.echo(f"✓ '{key}' is a valid key name.")
    else:
        for err in result.errors:
            click.echo(f"✗ {err}", err=True)
        raise SystemExit(1)


@validation_cmd.command("value")
@click.argument("value")
def value_cmd(value: str) -> None:
    """Check whether VALUE is acceptable as a secret value."""
    result = validate_value(value)
    if result.valid:
        click.echo("✓ Value is valid.")
    else:
        for err in result.errors:
            click.echo(f"✗ {err}", err=True)
        raise SystemExit(1)


@validation_cmd.command("pair")
@click.argument("key")
@click.argument("value")
def pair_cmd(key: str, value: str) -> None:
    """Validate a KEY/VALUE pair together."""
    result = validate_key_value(key, value)
    if result.valid:
        click.echo(f"✓ '{key}' and its value are both valid.")
    else:
        for err in result.errors:
            click.echo(f"✗ {err}", err=True)
        raise SystemExit(1)


def register(cli: click.Group) -> None:
    cli.add_command(validation_cmd)
