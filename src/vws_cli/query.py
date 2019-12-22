"""
A CLI for the Vuforia Cloud Recognition Service API.
"""

import click

from vws_cli.options.credentials import (
    client_access_key_option,
    client_secret_key_option,
)


@click.command(name='vuforia-cloud-reco')
@client_access_key_option
@client_secret_key_option
def vuforia_cloud_reco(client_access_key: str, client_secret_key: str) -> None:
    """
    Make a request to the Vuforia Cloud Recognition Service API.
    """
    assert client_access_key
    assert client_secret_key
