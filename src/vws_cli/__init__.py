"""A CLI for Vuforia Web Services."""

from importlib.metadata import PackageNotFoundError, version

import click
from beartype import beartype

from vws_cli.model_target import (
    create_model_target_dataset,
    delete_model_target_dataset,
    download_model_target_dataset,
    get_model_target_dataset_status,
    wait_for_model_target_dataset_generated,
)

__all__ = ["__version__"]

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
    """Manage Vuforia Model Target datasets."""


vws_group.add_command(cmd=create_model_target_dataset)
vws_group.add_command(cmd=delete_model_target_dataset)
vws_group.add_command(cmd=download_model_target_dataset)
vws_group.add_command(cmd=get_model_target_dataset_status)
vws_group.add_command(cmd=wait_for_model_target_dataset_generated)
