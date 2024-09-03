"""``click`` commands the VWS CLI."""

import contextlib
import dataclasses
import io
import sys
from collections.abc import Callable, Iterator
from pathlib import Path

import click
import yaml
from beartype import beartype
from vws import VWS
from vws.exceptions.base_exceptions import VWSError
from vws.exceptions.custom_exceptions import (
    OopsAnErrorOccurredPossiblyBadNameError,
    TargetProcessingTimeoutError,
)
from vws.exceptions.vws_exceptions import (
    AuthenticationFailureError,
    BadImageError,
    DateRangeError,
    FailError,
    ImageTooLargeError,
    MetadataTooLargeError,
    ProjectHasNoAPIAccessError,
    ProjectInactiveError,
    ProjectSuspendedError,
    RequestQuotaReachedError,
    RequestTimeTooSkewedError,
    TargetNameExistError,
    TargetQuotaReachedError,
    TargetStatusNotSuccessError,
    TargetStatusProcessingError,
    UnknownTargetError,
)

from vws_cli.options.credentials import (
    server_access_key_option,
    server_secret_key_option,
)
from vws_cli.options.targets import (
    ActiveFlagChoice,
    active_flag_option,
    application_metadata_option,
    target_id_option,
    target_image_option,
    target_name_option,
    target_width_option,
)


@beartype
def _get_error_message(exc: Exception) -> str:
    """Get an error message from a VWS exception."""
    if isinstance(exc, UnknownTargetError):
        return f'Error: Target "{exc.target_id}" does not exist.'

    if isinstance(exc, TargetNameExistError):
        return f'Error: There is already a target named "{exc.target_name}".'

    if isinstance(exc, TargetStatusNotSuccessError):
        return (
            f'Error: The target "{exc.target_id}" cannot be updated as it is '
            "in the processing state."
        )

    if isinstance(exc, TargetStatusProcessingError):
        return (
            f'Error: The target "{exc.target_id}" cannot be deleted as it is '
            "in the processing state."
        )

    exc_type_to_message: dict[type[Exception], str] = {
        AuthenticationFailureError: "The given secret key was incorrect.",
        BadImageError: "Error: The given image is corrupted or the format is not supported.",
        DateRangeError: "Error: There was a problem with the date details given in the request.",
        FailError: "Error: The request made to Vuforia was invalid and could not be processed. Check the given parameters.",
        ImageTooLargeError: "Error: The given image is too large.",
        MetadataTooLargeError: "Error: The given metadata is too large.",
        OopsAnErrorOccurredPossiblyBadNameError: "Error: There was an unknown error from Vuforia. This may be because there is a problem with the given name.",
        ProjectInactiveError: "Error: The project associated with the given keys is inactive.",
        RequestQuotaReachedError: "Error: The maximum number of API calls for this database has been reached.",
        RequestTimeTooSkewedError: "Error: Vuforia reported that the time given with this request was outside the expected range. This may be because the system clock is out of sync.",
        TargetProcessingTimeoutError: "Error: The target processing time has exceeded the allowed limit.",
        TargetQuotaReachedError: "Error: The maximum number of targets for this database has been reached.",
        ProjectSuspendedError: "Error: The request could not be completed because this database has been suspended.",
        ProjectHasNoAPIAccessError: "Error: The request could not be completed because this database is not allowed to make API requests.",
    }

    return exc_type_to_message[type(exc)]


@beartype
@contextlib.contextmanager
def handle_vws_exceptions() -> Iterator[None]:
    """Show error messages and catch exceptions from ``VWS-Python``."""
    error_message = ""

    try:
        yield
    except (
        VWSError,
        OopsAnErrorOccurredPossiblyBadNameError,
        TargetProcessingTimeoutError,
    ) as exc:
        error_message = _get_error_message(exc=exc)
    else:
        return

    click.echo(message=error_message, err=True)
    sys.exit(1)


def base_vws_url_option(command: Callable[..., None]) -> Callable[..., None]:
    """An option decorator for choosing the base VWS URL."""
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        "--base-vws-url",
        type=click.STRING,
        default="https://vws.vuforia.com",
        help="The base URL for the VWS API.",
        show_default=True,
    )

    function: Callable[..., None] = click_option_function(command)
    return function


@click.command(name="get-target-record")
@server_access_key_option
@server_secret_key_option
@target_id_option
@base_vws_url_option
@handle_vws_exceptions()
def get_target_record(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
) -> None:
    """Get a target record.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#target-record.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )
    record = vws_client.get_target_record(target_id=target_id).target_record

    yaml_record = yaml.dump(data=dataclasses.asdict(obj=record))
    click.echo(message=yaml_record)


@click.command(name="list-targets")
@server_access_key_option
@server_secret_key_option
@handle_vws_exceptions()
@base_vws_url_option
def list_targets(
    server_access_key: str,
    server_secret_key: str,
    base_vws_url: str,
) -> None:
    """List targets.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#details-list.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )
    targets = vws_client.list_targets()
    yaml_list = yaml.dump(data=targets)
    click.echo(message=yaml_list)


@click.command(name="get-duplicate-targets")
@server_access_key_option
@server_secret_key_option
@target_id_option
@handle_vws_exceptions()
@base_vws_url_option
def get_duplicate_targets(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
) -> None:
    """Get a list of potential duplicate targets.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#check.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )
    record = vws_client.get_duplicate_targets(target_id=target_id)

    yaml_record = yaml.dump(data=record)
    click.echo(message=yaml_record)


@click.command(name="get-database-summary-report")
@server_access_key_option
@server_secret_key_option
@handle_vws_exceptions()
@base_vws_url_option
def get_database_summary_report(
    server_access_key: str,
    server_secret_key: str,
    base_vws_url: str,
) -> None:
    """Get a database summary report.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#summary-report.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )
    report = vws_client.get_database_summary_report()
    yaml_report = yaml.dump(data=dataclasses.asdict(obj=report))
    click.echo(message=yaml_report)


@click.command(name="get-target-summary-report")
@server_access_key_option
@server_secret_key_option
@target_id_option
@handle_vws_exceptions()
@base_vws_url_option
def get_target_summary_report(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
) -> None:
    """Get a target summary report.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#retrieve-report.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )
    report = vws_client.get_target_summary_report(target_id=target_id)
    report_dict = dataclasses.asdict(obj=report)
    report_dict["status"] = report_dict["status"].value
    report_dict["upload_date"] = str(report_dict["upload_date"])
    yaml_summary_report = yaml.dump(data=report_dict)
    click.echo(message=yaml_summary_report)


@click.command(name="delete-target")
@server_access_key_option
@server_secret_key_option
@target_id_option
@handle_vws_exceptions()
@base_vws_url_option
def delete_target(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
) -> None:
    """Delete a target.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#delete.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )

    vws_client.delete_target(target_id=target_id)


@click.command(name="add-target")
@target_width_option(required=True)
@application_metadata_option
@server_access_key_option
@server_secret_key_option
@target_name_option(required=True)
@target_image_option(required=True)
@active_flag_option(allow_none=False)
@handle_vws_exceptions()
@base_vws_url_option
def add_target(
    server_access_key: str,
    server_secret_key: str,
    name: str,
    width: float,
    image_file_path: Path,
    active_flag_choice: ActiveFlagChoice,
    base_vws_url: str,
    application_metadata: str | None = None,
) -> None:
    """Add a target.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#add
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )

    image_bytes = image_file_path.read_bytes()
    image = io.BytesIO(initial_bytes=image_bytes)

    active_flag = {
        ActiveFlagChoice.TRUE: True,
        ActiveFlagChoice.FALSE: False,
    }[active_flag_choice]

    target_id = vws_client.add_target(
        name=name,
        width=width,
        image=image,
        active_flag=active_flag,
        application_metadata=application_metadata,
    )

    click.echo(message=target_id)


@click.command(name="update-target")
@target_width_option(required=False)
@application_metadata_option
@server_access_key_option
@server_secret_key_option
@target_name_option(required=False)
@target_image_option(required=False)
@active_flag_option(allow_none=True)
@target_id_option
@handle_vws_exceptions()
@base_vws_url_option
def update_target(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    image_file_path: Path | None,
    base_vws_url: str,
    name: str | None = None,
    application_metadata: str | None = None,
    active_flag_choice: ActiveFlagChoice | None = None,
    width: float | None = None,
) -> None:
    """Update a target.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api#update
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )

    if image_file_path is None:
        image = None
    else:
        image_bytes = image_file_path.read_bytes()
        image = io.BytesIO(initial_bytes=image_bytes)

    active_flag = {
        ActiveFlagChoice.TRUE: True,
        ActiveFlagChoice.FALSE: False,
        None: None,
    }[active_flag_choice]

    vws_client.update_target(
        name=name,
        target_id=target_id,
        image=image,
        application_metadata=application_metadata,
        active_flag=active_flag,
        width=width,
    )


_SECONDS_BETWEEN_REQUESTS_DEFAULT = 0.2

_SECONDS_BETWEEN_REQUESTS_HELP = (
    "The number of seconds to wait between requests made while polling the "
    "target status. "
    f"We wait {_SECONDS_BETWEEN_REQUESTS_DEFAULT} seconds by default, rather "
    "than less, than that to decrease the number of calls made to the API, to "
    "decrease the likelihood of hitting the request quota."
)

_TIMEOUT_SECONDS_HELP = (
    "The maximum number of seconds to wait for the target to be processed."
)


@click.command(name="wait-for-target-processed")
@click.option(
    "--seconds-between-requests",
    type=click.FloatRange(min=0.05),
    default=_SECONDS_BETWEEN_REQUESTS_DEFAULT,
    help=_SECONDS_BETWEEN_REQUESTS_HELP,
    show_default=True,
)
@click.option(
    "--timeout-seconds",
    type=click.FloatRange(min=0.05),
    default=300,
    help=_TIMEOUT_SECONDS_HELP,
    show_default=True,
)
@server_access_key_option
@server_secret_key_option
@target_id_option
@base_vws_url_option
@handle_vws_exceptions()
def wait_for_target_processed(
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    seconds_between_requests: float,
    base_vws_url: str,
    timeout_seconds: float,
) -> None:
    """Wait for a target to be "processed". This is done by polling the VWS API."""
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
    )

    try:
        vws_client.wait_for_target_processed(
            target_id=target_id,
            seconds_between_requests=seconds_between_requests,
            timeout_seconds=timeout_seconds,
        )
    except TargetProcessingTimeoutError:
        click.echo(
            message=f"Timeout of {timeout_seconds} seconds reached.",
            err=True,
        )
        sys.exit(1)
