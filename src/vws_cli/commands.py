"""
``click`` commands the VWS CLI.
"""

import io
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple

import click
import wrapt
import yaml
from vws import VWS
from vws.exceptions import TargetProcessingTimeout, UnknownTarget

from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)
from vws_cli.options.targets import (
    target_id_option,
    target_image_option,
    target_name_option,
    target_width_option,
)


@wrapt.decorator
def _handle_unknown_target(
    wrapped: Callable[..., str],
    instance: Any,
    args: Tuple,
    kwargs: Dict,
) -> None:
    assert not instance  # This is to satisfy the "vulture" linter.
    try:
        wrapped(*args, **kwargs)
    except UnknownTarget as exc:
        click.echo(f'Target "{exc.target_id}" does not exist.', err=True)
        sys.exit(1)


@click.command(name='get-target-record')
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_unknown_target
def get_target_record(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
) -> None:
    """
    Get a target record.

    \b
    See
    https://library.vuforia.com/articles/Solution/How-To-Use-the-Vuforia-Web-Services-API.htm#How-To-Retrieve-a-Target-Record.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    record = vws_client.get_target_record(target_id=target_id)

    yaml_record = yaml.dump(record)
    click.echo(yaml_record)


@click.command(name='list-targets')
@server_access_key_option
@server_secret_key_option
def list_targets(
    server_access_key: str,
    server_secret_key: str,
) -> None:
    """
    List targets.

    \b
    See
    https://library.vuforia.com/articles/Solution/How-To-Use-the-Vuforia-Web-Services-API.htm#How-To-Get-a-Target-List-for-a-Cloud-Database.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    targets = vws_client.list_targets()
    for target_id in targets:
        click.echo(target_id)


@click.command(name='get-duplicate-targets')
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_unknown_target
def get_duplicate_targets(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
) -> None:
    """
    Get a list of potential duplicate targets.

    \b
    See
    https://library.vuforia.com/articles/Solution/How-To-Use-the-Vuforia-Web-Services-API.htm#how-to-check-for-similar-targets.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    record = vws_client.get_duplicate_targets(target_id=target_id)

    yaml_record = yaml.dump(record)
    click.echo(yaml_record)


@click.command(name='get-database-summary-report')
@server_access_key_option
@server_secret_key_option
def get_database_summary_report(
    server_access_key: str,
    server_secret_key: str,
) -> None:
    """
    Get a database summary report.

    \b
    See
    https://library.vuforia.com/articles/Solution/How-To-Use-the-Vuforia-Web-Services-API.htm#How-To-Get-a-Database-Summary-Report.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    report = vws_client.get_database_summary_report()
    yaml_report = yaml.dump(report)
    click.echo(yaml_report)


@click.command(name='get-target-summary-report')
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_unknown_target
def get_target_summary_report(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
) -> None:
    """
    Get a target summary report.

    \b
    See
    https://library.vuforia.com/articles/Solution/How-To-Use-the-Vuforia-Web-Services-API.htm#How-To-Retrieve-a-Target-Summary-Report.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    report = vws_client.get_target_summary_report(target_id=target_id)
    yaml_summary_report = yaml.dump(report)
    click.echo(yaml_summary_report)


@click.command(name='delete-target')
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_unknown_target
def delete_target(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
) -> None:
    """
    Delete a target.

    \b
    See
    https://library.vuforia.com/articles/Solution/How-To-Use-the-Vuforia-Web-Services-API.htm#How-To-Delete-a-Target.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )

    vws_client.delete_target(target_id=target_id)


@click.command(name='add-target')
@server_access_key_option
@server_secret_key_option
@target_name_option
@target_width_option
@target_image_option
def add_target(
    server_access_key: str,
    server_secret_key: str,
    name: str,
    width: float,
    image_file_path: Path,
    application_metadata: Optional[str] = None,
    active_flag_false: bool = False,
) -> None:
    """
    Add a target.

    \b
    See
    https://library.vuforia.com/articles/Solution/How-To-Use-the-Vuforia-Web-Services-API#How-To-Add-a-Target
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )

    image = io.BytesIO(image_file_path.read_bytes())

    target_id = vws_client.add_target(
        name=name,
        width=width,
        image=image,
        active_flag=not active_flag_false,
        application_metadata=application_metadata,
    )

    click.echo(target_id)


_SECONDS_BETWEEN_REQUESTS_DEFAULT = 0.2

_SECONDS_BETWEEN_REQUESTS_HELP = (
    'The number of seconds to wait between requests made while polling the '
    'target status. '
    f'We wait {_SECONDS_BETWEEN_REQUESTS_DEFAULT} seconds by default, rather '
    'than less, than that to decrease the number of calls made to the API, to '
    'decrease the likelihood of hitting the request quota.'
)

_TIMEOUT_SECONDS_HELP = (
    'The maximum number of seconds to wait for the target to be processed.'
)


@click.command(name='wait-for-target-processed')
@click.option(
    '--seconds-between-requests',
    type=click.FloatRange(min=0.05),
    default=_SECONDS_BETWEEN_REQUESTS_DEFAULT,
    help=_SECONDS_BETWEEN_REQUESTS_HELP,
    show_default=True,
)
@click.option(
    '--timeout-seconds',
    type=click.FloatRange(min=0.05),
    default=300,
    help=_TIMEOUT_SECONDS_HELP,
    show_default=True,
)
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_unknown_target
def wait_for_target_processed(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    seconds_between_requests: float,
    timeout_seconds: float,
) -> None:
    """
    Wait for a target to be "processed".
    This is done by polling the VWS API.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )

    try:
        vws_client.wait_for_target_processed(
            target_id=target_id,
            seconds_between_requests=seconds_between_requests,
            timeout_seconds=timeout_seconds,
        )
    except TargetProcessingTimeout:
        click.echo(f'Timeout of {timeout_seconds} seconds reached.', err=True)
        sys.exit(1)
