"""A CLI for the Vuforia Cloud Recognition Service API."""

import contextlib
import dataclasses
import io
import sys
from collections.abc import Iterator
from pathlib import Path

import click
import yaml
from beartype import beartype
from vws import CloudRecoService
from vws.exceptions.cloud_reco_exceptions import (
    AuthenticationFailureError,
    BadImageError,
    InactiveProjectError,
    RequestTimeTooSkewedError,
)
from vws.exceptions.custom_exceptions import (
    RequestEntityTooLargeError,
)
from vws.include_target_data import CloudRecoIncludeTargetData

from vws_cli import __version__
from vws_cli.options.credentials import (
    client_access_key_option,
    client_secret_key_option,
)
from vws_cli.options.timeout import (
    connection_timeout_seconds_option,
    read_timeout_seconds_option,
)


@beartype
@contextlib.contextmanager
def _handle_vwq_exceptions() -> Iterator[None]:
    """Show error messages and catch exceptions from ``VWS-Python``."""
    try:
        yield
    except BadImageError:
        error_message = (
            "Error: The given image is corrupted or the format is not "
            "supported."
        )
    except InactiveProjectError:
        error_message = (
            "Error: The project associated with the given keys is inactive."
        )
    except AuthenticationFailureError:
        error_message = "The given secret key was incorrect."
    except RequestTimeTooSkewedError:
        error_message = (
            "Error: Vuforia reported that the time given with this request "
            "was outside the expected range. "
            "This may be because the system clock is out of sync."
        )
    except RequestEntityTooLargeError:
        error_message = "Error: The given image is too large."
    else:
        return

    click.echo(message=error_message, err=True)
    sys.exit(1)


_image_argument = click.argument(
    "image",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        path_type=Path,
    ),
)

_MAX_NUM_RESULTS_DEFAULT = 50
_max_num_results_option = click.option(
    "--max-num-results",
    type=click.IntRange(min=1, max=_MAX_NUM_RESULTS_DEFAULT),
    default=1,
    help=(
        "The maximum number of matching targets to be returned. "
        f"Must be <= {_MAX_NUM_RESULTS_DEFAULT}."
    ),
    show_default=True,
)


_include_target_data_option = click.option(
    "--include-target-data",
    type=click.Choice(
        choices=CloudRecoIncludeTargetData,
        case_sensitive=False,
    ),
    default=CloudRecoIncludeTargetData.TOP.lower(),
    help=(
        "Whether target_data records shall be returned for the matched "
        "targets. Accepted values are top (default value, only return "
        "target_data for top ranked match), none (return no target_data), "
        "all (for all matched targets)."
    ),
    show_default=True,
)

_base_vwq_url_option = click.option(
    "--base-vwq-url",
    type=click.STRING,
    default="https://cloudreco.vuforia.com",
    help="The base URL for the VWQ API.",
    show_default=True,
)


@click.command(name="vuforia-cloud-reco")
@_image_argument
@client_access_key_option
@client_secret_key_option
@_include_target_data_option
@_max_num_results_option
@_base_vwq_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_vwq_exceptions()
# We set the ``version`` parameter because in PyInstaller binaries,
# ``pkg_resources`` is not available.
#
# Click uses ``pkg_resources`` to determine the version if it is not given.
@click.version_option(version=__version__)
@beartype
def vuforia_cloud_reco(
    *,
    image: Path,
    client_access_key: str,
    client_secret_key: str,
    max_num_results: int,
    include_target_data: CloudRecoIncludeTargetData,
    base_vwq_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Make a request to the Vuforia Cloud Recognition Service API."""
    client = CloudRecoService(
        client_access_key=client_access_key,
        client_secret_key=client_secret_key,
        base_vwq_url=base_vwq_url,
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )
    query_result = client.query(
        image=io.BytesIO(initial_bytes=image.read_bytes()),
        max_num_results=max_num_results,
        include_target_data=include_target_data,
    )
    query_result_dict_list = [
        dataclasses.asdict(obj=res) for res in query_result
    ]
    yaml_list = yaml.dump(data=query_result_dict_list)
    click.echo(message=yaml_list)
