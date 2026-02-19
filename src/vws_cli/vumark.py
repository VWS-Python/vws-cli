"""``click`` command for VuMark generation."""

import contextlib
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

import click
from beartype import beartype
from vws import VuMarkService
from vws.exceptions.base_exceptions import VWSError
from vws.exceptions.custom_exceptions import ServerError
from vws.exceptions.vumark_exceptions import (
    InvalidVuMarkInstanceIdError,
    VuMarkQuotaExceededError,
)
from vws.exceptions.vws_exceptions import (
    AuthenticationFailureError,
    RequestTimeTooSkewedError,
    UnknownTargetError,
)
from vws.vumark import VuMarkOutputFormat

from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)
from vws_cli.options.targets import target_id_option
from vws_cli.options.timeout import (
    connection_timeout_seconds_option,
    read_timeout_seconds_option,
)


@beartype
def _get_vumark_error_message(exc: Exception) -> str:
    """Get an error message from a VuMark exception."""
    if isinstance(exc, UnknownTargetError):
        return f'Error: Target "{exc.target_id}" does not exist.'

    if isinstance(exc, InvalidVuMarkInstanceIdError):
        return "Error: The given instance ID is invalid."

    exc_type_to_message: dict[type[Exception], str] = {
        AuthenticationFailureError: "The given secret key was incorrect.",
        RequestTimeTooSkewedError: (
            "Error: Vuforia reported that the time given with this request "
            "was outside the expected range. "
            "This may be because the system clock is out of sync."
        ),
        ServerError: (
            "Error: There was an unknown error from Vuforia. "
            "This may be because there is a problem with the given name."
        ),
        VuMarkQuotaExceededError: (
            "Error: The VuMark generation quota has been reached."
        ),
    }

    return exc_type_to_message[type(exc)]


@beartype
@contextlib.contextmanager
def _handle_vumark_exceptions() -> Iterator[None]:
    """Show error messages and catch exceptions from ``VWS-Python``."""
    error_message = ""

    try:
        yield
    except (
        VWSError,
        ServerError,
    ) as exc:
        error_message = _get_vumark_error_message(exc=exc)
    else:
        return

    click.echo(message=error_message, err=True)
    sys.exit(1)


@beartype
def _base_vws_url_option(command: Callable[..., None]) -> Callable[..., None]:
    """An option decorator for choosing the base VWS URL."""
    click_option_function = click.option(
        "--base-vws-url",
        type=click.STRING,
        default="https://vws.vuforia.com",
        help="The base URL for the VWS API.",
        show_default=True,
    )

    return click_option_function(command)


@click.command(name="generate-vumark")
@server_access_key_option
@server_secret_key_option
@target_id_option
@click.option(
    "--instance-id",
    type=str,
    required=True,
    help="The instance ID to encode in the VuMark.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(choices=VuMarkOutputFormat, case_sensitive=False),
    default=VuMarkOutputFormat.SVG.lower(),
    help="The output format for the generated VuMark.",
    show_default=True,
)
@click.option(
    "--output",
    "output_file_path",
    type=click.Path(
        dir_okay=False,
        writable=True,
        path_type=Path,
    ),
    required=True,
    help="The path to write the generated VuMark to.",
)
@_handle_vumark_exceptions()
@_base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def generate_vumark(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    instance_id: str,
    output_format: VuMarkOutputFormat,
    output_file_path: Path,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Generate a VuMark instance.

    \b
    See
    https://developer.vuforia.com/library/vuforia-engine/web-api/vumark-generation-web-api/
    """
    vumark_client = VuMarkService(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )

    vumark_data = vumark_client.generate_vumark(
        target_id=target_id,
        instance_id=instance_id,
        output_format=output_format,
    )

    output_file_path.write_bytes(vumark_data)
