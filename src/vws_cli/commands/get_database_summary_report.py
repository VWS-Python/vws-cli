import click
import yaml
from vws import VWS

from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)


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
