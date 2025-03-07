"""
A CLI for Vuforia Web Services.
"""

from importlib.metadata import PackageNotFoundError, version

import click
from beartype import beartype

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

_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

try:
    __version__ = version(distribution_name=__name__)
except PackageNotFoundError:  # pragma: no cover
    # When pkg_resources and git tags are not available,
    # for example in a PyInstaller binary,
    # we write the file ``_setuptools_scm_version.py`` on ``pip install``.
    from ._setuptools_scm_version import __version__


@click.group(name="vws", context_settings=_CONTEXT_SETTINGS)
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
@click.version_option(version=__version__)
@beartype
def vws_group() -> None:
    """
    Manage a Vuforia Web Services cloud database.
    """


vws_group.add_command(cmd=add_target)
vws_group.add_command(cmd=delete_target)
vws_group.add_command(cmd=get_database_summary_report)
vws_group.add_command(cmd=get_duplicate_targets)
vws_group.add_command(cmd=get_target_record)
vws_group.add_command(cmd=get_target_summary_report)
vws_group.add_command(cmd=list_targets)
vws_group.add_command(cmd=update_target)
vws_group.add_command(cmd=wait_for_target_processed)
