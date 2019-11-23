import click
import yaml
from vws import VWS

from vws_cli.error_handlers import handle_unknown_target
from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)
from vws_cli.options.targets import target_id_option


@click.command(name='get-duplicate-targets')
@server_access_key_option
@server_secret_key_option
@target_id_option
@handle_unknown_target
def get_duplicate_targets(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
) -> None:
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
    )
    record = vws_client.get_duplicate_targets(target_id=target_id)

    yaml_record = yaml.dump(record)
    click.echo(yaml_record)
