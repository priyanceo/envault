"""Register bookmark commands with the main CLI."""

from __future__ import annotations

from envault.cli_bookmarks import bookmarks_cmd


def register(cli) -> None:
    """Attach the bookmarks command group to *cli*."""
    cli.add_command(bookmarks_cmd)
