"""``click`` command for VuMark generation."""

import contextlib
import sys
from collections.abc import Iterator
from enum import StrEnum, unique
from pathlib import Path

import click
from beartype import beartype
from vws import VuMarkService
from vws.exceptions.base_exceptions import VWSError
from vws.exceptions.custom_exceptions import ServerError
from vws.exceptions.vws_exceptions import (
    AuthenticationFailureError,
    FailError,
    InvalidInstanceIdError,
    InvalidTargetTypeError,
    ProjectHasNoAPIAccessError,
    ProjectInactiveError,
    ProjectSuspendedError,
    RequestQuotaReachedError,
    RequestTimeTooSkewedError,
    TargetStatusNotSuccessError,
    UnknownTargetError,
)
from vws.vumark_accept import VuMarkAccept

from vws_cli import __version__
from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)
from vws_cli.options.targets import target_id_option
from vws_cli.options.timeout import (
    connection_timeout_seconds_option,
    read_timeout_seconds_option,
)
from vws_cli.options.vws import base_vws_url_option


@beartype
@unique
class VuMarkFormatChoice(StrEnum):
    """Choices for the VuMark output format."""

    PNG = "png"
    SVG = "svg"
    PDF = "pdf"


_FORMAT_CHOICE_TO_ACCEPT: dict[VuMarkFormatChoice, VuMarkAccept] = {
    VuMarkFormatChoice.PNG: VuMarkAccept.PNG,
    VuMarkFormatChoice.SVG: VuMarkAccept.SVG,
    VuMarkFormatChoice.PDF: VuMarkAccept.PDF,
}


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
        if isinstance(exc, UnknownTargetError):
            error_message = f'Error: Target "{exc.target_id}" does not exist.'  # pylint: disable=no-member
        elif isinstance(exc, TargetStatusNotSuccessError):  # pragma: no cover
            error_message = (
                f'Error: The target "{exc.target_id}" is not in the success '  # pylint: disable=no-member
                "state and cannot be used to generate a VuMark instance."
            )
        elif isinstance(exc, InvalidInstanceIdError):
            error_message = "Error: The given instance ID is invalid."
        else:  # pragma: no cover
            exc_type_to_message: dict[type[Exception], str] = {
                InvalidTargetTypeError: (
                    "Error: The target is not a VuMark template target."
                ),
                AuthenticationFailureError: "The given secret key was incorrect.",
                FailError: (
                    "Error: The request made to Vuforia was invalid and could not be "
                    "processed. Check the given parameters."
                ),
                RequestTimeTooSkewedError: (
                    "Error: Vuforia reported that the time given with this request "
                    "was outside the expected range. "
                    "This may be because the system clock is out of sync."
                ),
                ServerError: "Error: There was an unknown error from Vuforia.",
                ProjectInactiveError: (
                    "Error: The project associated with the given keys is inactive."
                ),
                RequestQuotaReachedError: (
                    "Error: The maximum number of API calls for this database has "
                    "been reached."
                ),
                ProjectSuspendedError: (
                    "Error: The request could not be completed because this "
                    "database has been suspended."
                ),
                ProjectHasNoAPIAccessError: (
                    "Error: The request could not be completed because this "
                    "database is not allowed to make API requests."
                ),
            }
            error_message = exc_type_to_message.get(
                type(exc), "Error: There was an unexpected error from Vuforia."
            )
    else:
        return

    click.echo(message=error_message, err=True)
    sys.exit(1)


@click.command(name="vumark")
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
    "format_choice",
    type=click.Choice(choices=VuMarkFormatChoice, case_sensitive=False),
    default=VuMarkFormatChoice.PNG.lower(),
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
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@click.version_option(version=__version__)
@beartype
def generate_vumark(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    instance_id: str,
    format_choice: VuMarkFormatChoice,
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

    accept = _FORMAT_CHOICE_TO_ACCEPT[format_choice]

    vumark_data = vumark_client.generate_vumark_instance(
        target_id=target_id,
        instance_id=instance_id,
        accept=accept,
    )

    output_file_path.write_bytes(data=vumark_data)
