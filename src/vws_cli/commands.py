"""``click`` commands the VWS CLI."""

import calendar
import contextlib
import dataclasses
import datetime
import io
import sys
from collections.abc import Generator
from pathlib import Path
from zoneinfo import ZoneInfo

import click
import yaml
from beartype import beartype
from vws import VWS
from vws.exceptions.base_exceptions import VWSError
from vws.exceptions.custom_exceptions import (
    RecoCountsReportDownloadError,
    RecoCountsReportTimeoutError,
    ServerError,
    TargetProcessingTimeoutError,
)

from vws_cli._error_handling import get_error_message
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
from vws_cli.options.timeout import (
    connection_timeout_seconds_option,
    read_timeout_seconds_option,
)
from vws_cli.options.vws import base_vws_url_option, database_id_option


@beartype
@contextlib.contextmanager
def _handle_vws_exceptions() -> Generator[None]:
    """Show error messages and catch exceptions from ``VWS-Python``."""
    error_message = ""
    error_stream = sys.stderr

    try:
        yield
    except (
        VWSError,
        RecoCountsReportDownloadError,
        RecoCountsReportTimeoutError,
        ServerError,
        TargetProcessingTimeoutError,
    ) as exc:
        error_message = get_error_message(exc=exc)
    else:
        return

    click.echo(message=error_message, file=error_stream)
    sys.exit(1)


@click.command(name="get-target-record")
@server_access_key_option
@server_secret_key_option
@target_id_option
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_vws_exceptions()
@beartype
def get_target_record(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )
    record = vws_client.get_target_record(target_id=target_id).target_record

    yaml_record = yaml.dump(data=dataclasses.asdict(obj=record))
    click.echo(message=yaml_record)


@click.command(name="list-targets")
@server_access_key_option
@server_secret_key_option
@_handle_vws_exceptions()
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def list_targets(
    *,
    server_access_key: str,
    server_secret_key: str,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )
    targets = vws_client.list_targets()
    yaml_list = yaml.dump(data=targets)
    click.echo(message=yaml_list)


@click.command(name="get-duplicate-targets")
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_vws_exceptions()
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def get_duplicate_targets(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )
    record = vws_client.get_duplicate_targets(target_id=target_id)

    yaml_record = yaml.dump(data=record)
    click.echo(message=yaml_record)


@click.command(name="get-database-summary-report")
@server_access_key_option
@server_secret_key_option
@_handle_vws_exceptions()
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def get_database_summary_report(
    *,
    server_access_key: str,
    server_secret_key: str,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )
    report = vws_client.get_database_summary_report()
    yaml_report = yaml.dump(data=dataclasses.asdict(obj=report))
    click.echo(message=yaml_report)


@click.command(name="get-target-summary-report")
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_vws_exceptions()
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def get_target_summary_report(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )
    report = vws_client.get_target_summary_report(target_id=target_id)
    report_dict = dataclasses.asdict(obj=report)
    report_dict["status"] = report_dict["status"].value
    report_dict["upload_date"] = str(object=report_dict["upload_date"])
    yaml_summary_report = yaml.dump(data=report_dict)
    click.echo(message=yaml_summary_report)


@click.command(name="delete-target")
@server_access_key_option
@server_secret_key_option
@target_id_option
@_handle_vws_exceptions()
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def delete_target(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
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
@_handle_vws_exceptions()
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def add_target(
    *,
    server_access_key: str,
    server_secret_key: str,
    name: str,
    width: float,
    image_file_path: Path,
    active_flag_choice: ActiveFlagChoice,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
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
@_handle_vws_exceptions()
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@beartype
def update_target(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    image_file_path: Path | None,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
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
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
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
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_vws_exceptions()
@beartype
def wait_for_target_processed(
    *,
    server_access_key: str,
    server_secret_key: str,
    target_id: str,
    seconds_between_requests: float,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
    timeout_seconds: float,
) -> None:
    """Wait for a target to be "processed". This is done by polling the VWS
    API.
    """
    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )

    vws_client.wait_for_target_processed(
        target_id=target_id,
        seconds_between_requests=seconds_between_requests,
        timeout_seconds=timeout_seconds,
    )


_MONTH_FORMAT = "%Y-%m"

_REPORT_SECONDS_BETWEEN_REQUESTS_HELP = (
    "The number of seconds to wait between requests made while polling for "
    "the report. "
    f"We wait {_SECONDS_BETWEEN_REQUESTS_DEFAULT} seconds by default, rather "
    "than less, than that to decrease the number of calls made to the API, to "
    "decrease the likelihood of hitting the request quota."
)

_REPORT_TIMEOUT_SECONDS_HELP = (
    "The maximum number of seconds to wait for the report to be generated."
)


@beartype
def _default_month() -> str:
    """Return the current month, in the form which ``--month`` takes."""
    now = datetime.datetime.now(tz=ZoneInfo(key="UTC"))
    return now.strftime(format=_MONTH_FORMAT)


@beartype
def _validate_month(
    ctx: click.Context,
    param: click.Parameter,
    value: str,
) -> datetime.date:
    """Turn a ``YYYY-mm`` string into the first day of that month."""
    # These are given by ``click``, and we do not use them.
    del ctx
    del param
    try:
        parsed = datetime.datetime.strptime(  # noqa: DTZ007
            value,
            _MONTH_FORMAT,
        )
    except ValueError as exc:
        message = f'"{value}" is not a month in the YYYY-mm form.'
        raise click.BadParameter(message=message) from exc
    return parsed.date()


@click.command(name="get-database-reco-counts-report")
@click.option(
    "--month",
    type=str,
    default=_default_month,
    callback=_validate_month,
    help=(
        "The month to get recognition counts for, in the YYYY-mm form. "
        "Vuforia accepts only the current month and the previous month."
    ),
    show_default="the current month",
)
@click.option(
    "--output",
    "output_file_path",
    type=click.Path(
        dir_okay=False,
        writable=True,
        path_type=Path,
    ),
    required=False,
    help=(
        "The path to write the CSV report to. By default, the report is "
        "written to stdout."
    ),
)
@click.option(
    "--no-wait",
    "no_wait",
    is_flag=True,
    default=False,
    help=(
        "Do not wait for the report to be generated. Instead, show the URL "
        "to download the report from once it has been generated."
    ),
)
@click.option(
    "--seconds-between-requests",
    type=click.FloatRange(min=0.05),
    default=_SECONDS_BETWEEN_REQUESTS_DEFAULT,
    help=_REPORT_SECONDS_BETWEEN_REQUESTS_HELP,
    show_default=True,
)
@click.option(
    "--timeout-seconds",
    type=click.FloatRange(min=0.05),
    default=300,
    help=_REPORT_TIMEOUT_SECONDS_HELP,
    show_default=True,
)
@server_access_key_option
@server_secret_key_option
@database_id_option
@base_vws_url_option
@connection_timeout_seconds_option
@read_timeout_seconds_option
@_handle_vws_exceptions()
@beartype
def get_database_reco_counts_report(
    *,
    server_access_key: str,
    server_secret_key: str,
    database_id: str,
    month: datetime.date,
    output_file_path: Path | None,
    no_wait: bool,
    seconds_between_requests: float,
    timeout_seconds: float,
    base_vws_url: str,
    connection_timeout_seconds: float,
    read_timeout_seconds: float,
) -> None:
    """Get a per-target recognition counts report for a database.

    The report is a CSV with a ``target_id,reco_count`` header. Vuforia
    generates the report in the background, so by default we wait for the
    report to be generated before downloading it.

    \b
    See
    https://developer.vuforia.com/library/web-api/cloud-targets-web-services-api.
    """
    if no_wait and output_file_path is not None:
        message = "--output cannot be used with --no-wait."
        raise click.UsageError(message=message)

    vws_client = VWS(
        server_access_key=server_access_key,
        server_secret_key=server_secret_key,
        base_vws_url=base_vws_url,
        database_id=database_id,
        request_timeout_seconds=(
            connection_timeout_seconds,
            read_timeout_seconds,
        ),
    )

    report_request = vws_client.request_database_reco_counts_report(
        year=month.year,
        month=calendar.Month(value=month.month),
    )

    if no_wait:
        click.echo(message=report_request.presigned_url)
        return

    report = vws_client.wait_for_reco_counts_report(
        presigned_url=report_request.presigned_url,
        seconds_between_requests=seconds_between_requests,
        timeout_seconds=timeout_seconds,
    )

    if output_file_path is None:
        click.echo(message=report.raw_csv, nl=False)
        return

    output_file_path.write_bytes(data=report.raw_csv)
