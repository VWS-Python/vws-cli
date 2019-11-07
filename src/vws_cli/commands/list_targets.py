import click
from vws import VWS

from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)


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
