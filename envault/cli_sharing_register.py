"""Registration helper — attach share_cmd to the root CLI.

Import this module in envault/cli.py to enable the `envault share` command group::

    from envault.cli_sharing_register import register
    register(cli)
"""

from envault.cli_sharing import share_cmd


def register(cli_group):
    """Attach the share command group to *cli_group*."""
    cli_group.add_command(share_cmd)
