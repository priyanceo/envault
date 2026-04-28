"""CLI commands for checking secret complexity in envault."""

import click
from envault.complexity import score_secret, enforce_complexity
from envault.storage import get_secret


@click.group(name="complexity")
def complexity_cmd():
    """Check and enforce secret value complexity."""


@complexity_cmd.command(name="check")
@click.argument("value")
@click.option("--min-score", default=2, show_default=True, help="Minimum score 0-4.")
def check_cmd(value: str, min_score: int):
    """Score the complexity of VALUE and report results."""
    result = score_secret(value)
    click.echo(f"Score : {result.score}/4  ({result.level})")
    if result.suggestions:
        click.echo("Tips  :")
        for tip in result.suggestions:
            click.echo(f"  - {tip}")
    if result.score < min_score:
        click.echo(f"Result: FAIL (minimum score required: {min_score})", err=True)
        raise SystemExit(1)
    click.echo("Result: PASS")


@complexity_cmd.command(name="audit")
@click.option("--vault-dir", envvar="ENVAULT_DIR", default=None, hidden=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--min-score", default=2, show_default=True, help="Minimum score 0-4.")
@click.argument("keys", nargs=-1)
def audit_cmd(vault_dir, password: str, min_score: int, keys):
    """Audit stored secrets and report weak ones."""
    from envault.storage import list_keys

    all_keys = list_keys(password, vault_dir=vault_dir)
    targets = list(keys) if keys else all_keys
    weak = []
    for key in targets:
        value = get_secret(key, password, vault_dir=vault_dir)
        if value is None:
            continue
        result = score_secret(value)
        if result.score < min_score:
            weak.append((key, result.score, result.level))

    if not weak:
        click.echo("All audited secrets meet the complexity requirement.")
        return

    click.echo(f"{'KEY':<30} {'SCORE':<6} LEVEL")
    click.echo("-" * 45)
    for key, sc, lvl in weak:
        click.echo(f"{key:<30} {sc:<6} {lvl}")
    click.echo(f"\n{len(weak)} weak secret(s) found.", err=True)
    raise SystemExit(1)


def register(cli):
    cli.add_command(complexity_cmd)
