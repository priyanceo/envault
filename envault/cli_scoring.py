"""CLI commands for vault-wide secret scoring."""

import click
from envault.scoring import score_key, score_all
from envault.storage import list_secrets


@click.group("score")
def scoring_cmd():
    """Score secrets by complexity, expiry, and other quality factors."""


@scoring_cmd.command("show")
@click.argument("key")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
def show_cmd(key: str, vault_dir: str, password: str):
    """Show the quality score for a single KEY."""
    result = score_key(key, vault_dir, password)
    if result is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Key          : {result.key}")
    click.echo(f"Complexity   : {result.complexity_score}/100")
    click.echo(f"Has expiry   : {'yes' if result.has_expiry else 'no'}")
    click.echo(f"Expired      : {'yes' if result.is_expired else 'no'}")
    click.echo(f"Overall score: {result.overall}/100")
    if result.suggestions:
        click.echo("Suggestions:")
        for s in result.suggestions:
            click.echo(f"  - {s}")


@scoring_cmd.command("audit")
@click.option("--vault-dir", envvar="ENVAULT_VAULT_DIR", required=True)
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--min-score", default=0, show_default=True,
              help="Only show keys with overall score below this threshold.")
def audit_cmd(vault_dir: str, password: str, min_score: int):
    """Audit all secrets and report their quality scores."""
    keys = list_secrets(vault_dir, password)
    if not keys:
        click.echo("Vault is empty.")
        return

    scores = score_all(vault_dir, password, keys)
    filtered = [
        s for s in scores.values()
        if min_score == 0 or s.overall < min_score
    ]
    if not filtered:
        click.echo("All secrets meet the minimum score threshold.")
        return

    filtered.sort(key=lambda s: s.overall)
    for s in filtered:
        status = "EXPIRED" if s.is_expired else "ok"
        click.echo(
            f"{s.key:<30} overall={s.overall:>3}/100  "
            f"complexity={s.complexity_score:>3}  [{status}]"
        )


def register(cli):
    cli.add_command(scoring_cmd)
