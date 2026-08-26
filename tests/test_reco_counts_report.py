"""Tests for the ``get-database-reco-counts-report`` command."""

import datetime
import uuid
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from click.testing import CliRunner
from mock_vws import MockVWS
from mock_vws.database import CloudDatabase
from vws import VWS
from vws.exceptions.custom_exceptions import RecoCountsReportNotReadyError

from vws_cli import vws_group

_EXPECTED_CSV = b"target_id,reco_count\r\n"

# The exit code which ``click`` uses for a usage error.
_USAGE_ERROR_EXIT_CODE = 2


def _month_string(*, months_ago: int) -> str:
    """Return a ``YYYY-mm`` string for a month relative to this month."""
    now = datetime.datetime.now(tz=ZoneInfo(key="UTC"))
    first_of_month = now.replace(day=1)
    for _ in range(months_ago):
        first_of_month = first_of_month.replace(day=1) - datetime.timedelta(
            days=1,
        )
    return first_of_month.strftime(format="%Y-%m")


def _base_commands(*, mock_database: CloudDatabase) -> list[str]:
    """Return the command and credential arguments for the report
    command.
    """
    return [
        "get-database-reco-counts-report",
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
        "--database-id",
        mock_database.database_id,
    ]


def test_get_database_reco_counts_report(
    *,
    mock_database: CloudDatabase,
) -> None:
    """The report is written to stdout.

    The ``mock_database`` fixture does not make the report available
    immediately, so this also shows that the command waits for the report.
    """
    runner = CliRunner()
    result = runner.invoke(
        cli=vws_group,
        args=_base_commands(mock_database=mock_database),
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    assert not result.stderr
    assert result.stdout_bytes == _EXPECTED_CSV


def test_report_is_not_available_immediately() -> None:
    """The command waits for a report which is not ready to download."""
    runner = CliRunner()
    mock_database = CloudDatabase()
    with MockVWS(processing_time_seconds=1) as mock:
        mock.add_cloud_database(cloud_database=mock_database)
        vws_client = VWS(
            server_access_key=mock_database.server_access_key,
            server_secret_key=mock_database.server_secret_key,
        )
        no_wait_result = runner.invoke(
            cli=vws_group,
            args=[*_base_commands(mock_database=mock_database), "--no-wait"],
            catch_exceptions=False,
            color=True,
        )
        assert no_wait_result.exit_code == 0
        presigned_url = no_wait_result.stdout.strip()
        with pytest.raises(expected_exception=RecoCountsReportNotReadyError):
            vws_client.download_reco_counts_report(
                presigned_url=presigned_url,
            )

        result = runner.invoke(
            cli=vws_group,
            args=_base_commands(mock_database=mock_database),
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 0
    assert result.stdout_bytes == _EXPECTED_CSV


def test_output_file(*, tmp_path: Path) -> None:
    """The report is written to the path given by ``--output``."""
    runner = CliRunner()
    mock_database = CloudDatabase()
    output_file_path = tmp_path / uuid.uuid4().hex
    with MockVWS(processing_time_seconds=0) as mock:
        mock.add_cloud_database(cloud_database=mock_database)
        result = runner.invoke(
            cli=vws_group,
            args=[
                *_base_commands(mock_database=mock_database),
                "--output",
                str(object=output_file_path),
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 0
    assert not result.stdout
    assert output_file_path.read_bytes() == _EXPECTED_CSV


def test_no_wait() -> None:
    """``--no-wait`` shows the URL to download the report from."""
    runner = CliRunner()
    mock_database = CloudDatabase()
    with MockVWS(processing_time_seconds=0) as mock:
        mock.add_cloud_database(cloud_database=mock_database)
        vws_client = VWS(
            server_access_key=mock_database.server_access_key,
            server_secret_key=mock_database.server_secret_key,
        )
        result = runner.invoke(
            cli=vws_group,
            args=[*_base_commands(mock_database=mock_database), "--no-wait"],
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        presigned_url = result.stdout.strip()
        report = vws_client.download_reco_counts_report(
            presigned_url=presigned_url,
        )

    assert report.raw_csv == _EXPECTED_CSV


def test_no_wait_with_output_file(
    *,
    mock_database: CloudDatabase,
    tmp_path: Path,
) -> None:
    """``--output`` cannot be used with ``--no-wait``."""
    runner = CliRunner()
    output_file_path = tmp_path / uuid.uuid4().hex
    result = runner.invoke(
        cli=vws_group,
        args=[
            *_base_commands(mock_database=mock_database),
            "--no-wait",
            "--output",
            str(object=output_file_path),
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    assert "--output cannot be used with --no-wait." in result.stderr
    assert not output_file_path.exists()


def test_previous_month() -> None:
    """A report can be requested for the previous month."""
    runner = CliRunner()
    mock_database = CloudDatabase()
    with MockVWS(processing_time_seconds=0) as mock:
        mock.add_cloud_database(cloud_database=mock_database)
        result = runner.invoke(
            cli=vws_group,
            args=[
                *_base_commands(mock_database=mock_database),
                "--month",
                _month_string(months_ago=1),
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 0
    assert result.stdout_bytes == _EXPECTED_CSV


def test_month_is_not_in_the_yyyy_mm_form(
    *,
    mock_database: CloudDatabase,
) -> None:
    """An error is shown for a month which is not in the ``YYYY-mm``
    form.
    """
    runner = CliRunner()
    result = runner.invoke(
        cli=vws_group,
        args=[
            *_base_commands(mock_database=mock_database),
            "--month",
            "not-a-month",
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == _USAGE_ERROR_EXIT_CODE
    expected_message = '"not-a-month" is not a month in the YYYY-mm form.'
    assert expected_message in result.stderr


def test_month_out_of_range(*, mock_database: CloudDatabase) -> None:
    """An error is shown for a month which Vuforia does not accept.

    Vuforia accepts only the current month and the previous month.
    """
    runner = CliRunner()
    result = runner.invoke(
        cli=vws_group,
        args=[
            *_base_commands(mock_database=mock_database),
            "--month",
            _month_string(months_ago=2),
        ],
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 1
    expected_stderr = (
        "Error: The request made to Vuforia was invalid and could not be "
        "processed. Check the given parameters.\n"
    )
    assert result.stderr == expected_stderr
    assert not result.stdout


def test_database_id_does_not_match(
    *,
    mock_database: CloudDatabase,
) -> None:
    """An error is shown when the given database ID is not the
    database's.
    """
    runner = CliRunner()
    commands = [
        "get-database-reco-counts-report",
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
        "--database-id",
        uuid.uuid4().hex,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 1
    expected_stderr = "The given secret key was incorrect.\n"
    assert result.stderr == expected_stderr
    assert not result.stdout


def test_timeout_reached() -> None:
    """An error is shown when the report is not generated in time."""
    runner = CliRunner()
    mock_database = CloudDatabase()
    timeout_seconds = 0.1
    with MockVWS(processing_time_seconds=60) as mock:
        mock.add_cloud_database(cloud_database=mock_database)
        result = runner.invoke(
            cli=vws_group,
            args=[
                *_base_commands(mock_database=mock_database),
                "--timeout-seconds",
                str(object=timeout_seconds),
                "--seconds-between-requests",
                "0.05",
            ],
            catch_exceptions=False,
            color=True,
        )

    assert result.exit_code == 1
    assert result.stderr == (
        "Error: The recognition counts report was not generated within the "
        "allowed limit.\n"
    )
    assert not result.stdout
