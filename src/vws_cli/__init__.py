import click
import sys
from typing import Callable
from vws import VWS
from vws.exceptions import UnknownTarget
import yaml

from .options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)


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



def target_id_option(
    command: Callable[..., None],
) -> Callable[..., None]:
    """
    An option decorator for XXX.
    """
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        '--target-id',
        type=str,
        help='XXX',
        required=True,
    )
    function: Callable[..., None] = click_option_function(command)
    return function




@click.command(name='list-targets')
@server_access_key_option
@server_secret_key_option
def list_targets(
    server_access_key: str,
    server_secret_key: str,
) -> None:
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    targets = vws_client.list_targets()
    for target_id in targets:
        click.echo(target_id)


@click.command(name='get-database-summary-report')
@server_access_key_option
@server_secret_key_option
def get_database_summary_report(
    server_access_key: str,
    server_secret_key: str,
) -> None:
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    report = vws_client.get_database_summary_report()
    yaml_report = yaml.dump(report)
    click.echo(yaml_report)


@click.command(name='get-target-record')
@server_access_key_option
@server_secret_key_option
@target_id_option
def get_target_record(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
) -> None:
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    try:
        record = vws_client.get_target_record(target_id=target_id)
    except UnknownTarget:
        click.echo(f'Target "{target_id}" does not exist.', err=True)
        sys.exit(1)

    yaml_record = yaml.dump(record)
    click.echo(yaml_record)


vws_group.add_command(list_targets)
vws_group.add_command(get_database_summary_report)
vws_group.add_command(get_target_record)
