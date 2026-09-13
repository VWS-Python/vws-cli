"""A CLI for Vuforia Web Services."""

import click
from beartype import beartype

from vws_cli._setuptools_scm_version import __version__
from vws_cli.commands import (
    add_target,
    delete_target,
    get_database_reco_counts_report,
    get_database_summary_report,
    get_duplicate_targets,
    get_target_record,
    get_target_summary_report,
    list_targets,
    update_target,
    wait_for_target_processed,
)
from vws_cli.model_target import (
    create_model_target_dataset,
    delete_model_target_dataset,
    download_model_target_dataset,
    get_model_target_dataset_status,
    wait_for_model_target_dataset_generated,
)

__all__ = ["__version__"]

_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(name="vws", context_settings=_CONTEXT_SETTINGS)
# Supply the build version so frozen binaries need no distribution metadata.
@click.version_option(version=__version__)
@beartype
def vws_group() -> None:
    """Manage a Vuforia Web Services cloud database."""


vws_group.add_command(cmd=add_target)
vws_group.add_command(cmd=create_model_target_dataset)
vws_group.add_command(cmd=delete_model_target_dataset)
vws_group.add_command(cmd=delete_target)
vws_group.add_command(cmd=download_model_target_dataset)
vws_group.add_command(cmd=get_database_reco_counts_report)
vws_group.add_command(cmd=get_database_summary_report)
vws_group.add_command(cmd=get_duplicate_targets)
vws_group.add_command(cmd=get_model_target_dataset_status)
vws_group.add_command(cmd=get_target_record)
vws_group.add_command(cmd=get_target_summary_report)
vws_group.add_command(cmd=list_targets)
vws_group.add_command(cmd=update_target)
vws_group.add_command(cmd=wait_for_model_target_dataset_generated)
vws_group.add_command(cmd=wait_for_target_processed)
