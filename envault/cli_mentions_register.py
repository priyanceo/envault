"""Registration shim so the main CLI can include the mentions command."""

from __future__ import annotations

import click

from envault.cli_mentions import mentions_cmd


def register(cli: click.Group) -> None:
    """Attach the mentions command group to *cli*."""
    cli.add_command(mentions_cmd)
