import sys

import click
import yaml
from vws import VWS
from vws.exceptions import UnknownTarget

from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)
from vws_cli.options.targets import target_id_option


@click.command(name='get-target-summary-report')
@server_access_key_option
@server_secret_key_option
@target_id_option
def get_target_summary_report(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
) -> None:
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    try:
        summary_report = vws_client.get_target_summary_report(target_id=target_id)
    except UnknownTarget:
        click.echo(f'Target "{target_id}" does not exist.', err=True)
        sys.exit(1)

    yaml_summary_report = yaml.dump(summary_report)
    click.echo(yaml_summary_report)
