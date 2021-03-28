"""
A CLI for Vuforia Web Services.
"""

from pathlib import Path

import click
from setuptools_scm import get_version

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

_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

try:
    __version__ = get_version(root='../..', relative_to=__file__)
except LookupError:  # pragma: no cover
    # When pkg_resources and git tags are not available,
    # for example in a PyInstaller binary,
    # we write the file ``_setuptools_scm_version.py`` on ``pip install``.
    _VERSION_FILE = Path(__file__).parent / '_setuptools_scm_version.txt'
    __version__ = _VERSION_FILE.read_text()


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
