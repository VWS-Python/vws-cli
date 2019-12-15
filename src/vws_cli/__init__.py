"""
A CLI for Vuforia Web Services.
"""

import click

from vws_cli.commands import (
    add_target,
    delete_target,
    get_database_summary_report,
    get_duplicate_targets,
    get_target_record,
    get_target_summary_report,
    list_targets,
    update_target,
    wait_for_target_processed,
)

from ._version import get_versions

_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
__version__ = get_versions()['version']  # type: ignore
del get_versions


@click.group(name='vws', context_settings=_CONTEXT_SETTINGS)
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
@click.version_option(version=__version__)
def vws_group() -> None:
    """
    Manage a Vuforia Web Services cloud database.
    """


vws_group.add_command(add_target)
vws_group.add_command(delete_target)
vws_group.add_command(get_database_summary_report)
vws_group.add_command(get_duplicate_targets)
vws_group.add_command(get_target_record)
vws_group.add_command(get_target_summary_report)
vws_group.add_command(list_targets)
vws_group.add_command(update_target)
vws_group.add_command(wait_for_target_processed)
