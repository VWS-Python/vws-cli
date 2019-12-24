"""
A CLI for the Vuforia Cloud Recognition Service API.
"""

import io
from pathlib import Path
from typing import Callable

import click
import click_pathlib
import yaml
from vws import CloudRecoService

from vws_cli import __version__
from vws_cli.options.credentials import (
    client_access_key_option,
    client_secret_key_option,
)


def image_argument(command: Callable[..., None]) -> Callable[..., None]:
    """
    An argument decorator for choosing a query image.
    """
    click_option_function = click.argument(
        'image',
        type=click_pathlib.Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
        ),
    )

    return click_option_function(command)


def max_num_results_option(
    command: Callable[..., None],
) -> Callable[..., None]:
    """
    An option decorator for choosing the maximum number of query results.
    """
    click_option_function = click.option(
        '--max-num-results',
        type=click.IntRange(min=1, max=50),
        default=1,
    )

    return click_option_function(command)


@click.command(name='vuforia-cloud-reco')
@image_argument
@client_access_key_option
@client_secret_key_option
@max_num_results_option
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
@click.version_option(version=__version__)
def vuforia_cloud_reco(
    image: Path,
    client_access_key: str,
    client_secret_key: str,
    max_num_results: int,
) -> None:
    """
    Make a request to the Vuforia Cloud Recognition Service API.
    """
    client = CloudRecoService(
        client_access_key=client_access_key,
        client_secret_key=client_secret_key,
    )
    query_result = client.query(
        image=io.BytesIO(image.read_bytes()),
        max_num_results=max_num_results,
    )
    yaml_list = yaml.dump(query_result)
    click.echo(yaml_list)
