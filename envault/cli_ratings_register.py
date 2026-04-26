"""Register the ratings command group with the main CLI."""
from envault.cli_ratings import ratings_cmd


def register(cli) -> None:  # noqa: ANN001
    cli.add_command(ratings_cmd)
