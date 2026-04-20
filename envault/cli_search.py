"""CLI commands for searching secrets."""

from __future__ import annotations

import click

from envault.search import search_by_pattern, search_by_tag


@click.group("search")
def search_cmd() -> None:
    """Search secrets by key pattern or tag."""


@search_cmd.command("pattern")
@click.argument("pattern")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--no-profiles", is_flag=True, default=False, help="Skip profile vaults.")
def pattern_cmd(pattern: str, vault_dir: str, password: str, no_profiles: bool) -> None:
    """Search secrets whose key matches PATTERN (supports glob wildcards)."""
    results = search_by_pattern(
        vault_dir, password, pattern, include_profiles=not no_profiles
    )
    if not results:
        click.echo("No secrets matched.")
        return
    for r in results:
        tags_str = f"  [{', '.join(r.tags)}]" if r.tags else ""
        click.echo(f"[{r.source}] {r.key}{tags_str}")


@search_cmd.command("tag")
@click.argument("tag")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--no-profiles", is_flag=True, default=False, help="Skip profile vaults.")
def tag_cmd(tag: str, vault_dir: str, password: str, no_profiles: bool) -> None:
    """Search secrets that have the given TAG."""
    results = search_by_tag(
        vault_dir, password, tag, include_profiles=not no_profiles
    )
    if not results:
        click.echo(f"No secrets found with tag '{tag}'.")
        return
    for r in results:
        tags_str = f"  [{', '.join(r.tags)}]" if r.tags else ""
        click.echo(f"[{r.source}] {r.key}{tags_str}")
