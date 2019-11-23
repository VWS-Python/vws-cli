"""
``click`` commands the VWS CLI.
"""

import sys
from typing import Any, Callable, Dict, Tuple

import click
import wrapt
import yaml
from vws import VWS
from vws.exceptions import UnknownTarget

from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)
from vws_cli.options.targets import target_id_option


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
