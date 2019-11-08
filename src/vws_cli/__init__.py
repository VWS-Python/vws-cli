import click

from vws_cli.commands.delete_target import delete_target
from vws_cli.commands.get_database_summary_report import (
    get_database_summary_report,
)
from vws_cli.commands.get_target_record import get_target_record
from vws_cli.commands.get_target_summary_report import get_target_summary_report
from vws_cli.commands.list_targets import list_targets

_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(name='vws', context_settings=_CONTEXT_SETTINGS)
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
# @click.version_option(version=vws_cli.__version__)
@click.version_option(version='0')
def vws_group() -> None:
    """
    Manage VWS.
    """


vws_group.add_command(list_targets)
vws_group.add_command(get_database_summary_report)
vws_group.add_command(get_target_record)
vws_group.add_command(delete_target)
vws_group.add_command(get_target_summary_report)
