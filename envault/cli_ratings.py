"""CLI commands for secret ratings."""
from __future__ import annotations

import click

from envault.ratings import get_rating, list_by_rating, remove_rating, set_rating


@click.group("ratings")
def ratings_cmd() -> None:
    """Rate secrets by importance (1–5 stars)."""


@ratings_cmd.command("set")
@click.argument("key")
@click.argument("stars", type=int)
@click.option("--password", "-p", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, hidden=True)
def set_cmd(key: str, stars: int, password: str, vault_dir: str | None) -> None:
    """Set a star rating (1–5) for KEY."""
    from pathlib import Path
    vd = Path(vault_dir) if vault_dir else None
    try:
        set_rating(key, stars, password, vault_dir=vd)
        click.echo(f"Rated '{key}': {stars} star(s).")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    except KeyError:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)


@ratings_cmd.command("get")
@click.argument("key")
@click.option("--vault-dir", default=None, hidden=True)
def get_cmd(key: str, vault_dir: str | None) -> None:
    """Show the star rating for KEY."""
    from pathlib import Path
    vd = Path(vault_dir) if vault_dir else None
    rating = get_rating(key, vault_dir=vd)
    if rating is None:
        click.echo(f"No rating set for '{key}'.", err=True)
        raise SystemExit(1)
    click.echo(f"{key}: {'★' * rating}{'☆' * (5 - rating)} ({rating}/5)")


@ratings_cmd.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=None, hidden=True)
def remove_cmd(key: str, vault_dir: str | None) -> None:
    """Remove the rating for KEY."""
    from pathlib import Path
    vd = Path(vault_dir) if vault_dir else None
    removed = remove_rating(key, vault_dir=vd)
    if removed:
        click.echo(f"Rating removed for '{key}'.")
    else:
        click.echo(f"No rating found for '{key}'.", err=True)
        raise SystemExit(1)


@ratings_cmd.command("list")
@click.option("--min", "min_stars", default=1, show_default=True, type=int)
@click.option("--max", "max_stars", default=5, show_default=True, type=int)
@click.option("--vault-dir", default=None, hidden=True)
def list_cmd(min_stars: int, max_stars: int, vault_dir: str | None) -> None:
    """List rated secrets, sorted by stars descending."""
    from pathlib import Path
    vd = Path(vault_dir) if vault_dir else None
    results = list_by_rating(min_stars, max_stars, vault_dir=vd)
    if not results:
        click.echo("No ratings found.")
        return
    for key, stars in results:
        click.echo(f"{key}: {'★' * stars}{'☆' * (5 - stars)} ({stars}/5)")
