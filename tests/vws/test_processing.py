"""Tests for `vws` processing commands."""

import io

from click.testing import CliRunner
from mock_vws import MockVWS
from mock_vws.database import CloudDatabase
from vws import VWS
from vws.reports import TargetStatuses

from vws_cli import vws_group


def test_wait_for_target_processed(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to use a command to wait for a target to be
    processed.
    """
    runner = CliRunner()
    target_id = vws_client.add_target(
        name="x",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    report = vws_client.get_target_summary_report(target_id=target_id)
    assert report.status == TargetStatuses.PROCESSING
    commands = [
        "wait-for-target-processed",
        "--target-id",
        target_id,
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    assert not bool(result.stdout)
    report = vws_client.get_target_summary_report(target_id=target_id)
    assert report.status != TargetStatuses.PROCESSING


def test_default_seconds_between_requests(
    high_quality_image: io.BytesIO,
) -> None:
    """By default, 0.2 seconds are waited between polling requests."""
    runner = CliRunner()
    with MockVWS(processing_time_seconds=0.5) as mock:
        mock_database = CloudDatabase()
        mock.add_cloud_database(cloud_database=mock_database)
        vws_client = VWS(
            server_access_key=mock_database.server_access_key,
            server_secret_key=mock_database.server_secret_key,
        )

        target_id = vws_client.add_target(
            name="x",
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )

        commands = [
            "wait-for-target-processed",
            "--target-id",
            target_id,
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert not bool(result.stdout)
        report = vws_client.get_database_summary_report()
        expected_requests = (
            # Add target request
            1
            +
            # Database summary request
            1
            +
            # Initial request
            1
            +
            # Request after 0.2 seconds - not processed
            1
            +
            # Request after 0.4 seconds - not processed
            # This assumes that there is less than 0.1 seconds taken
            # between the start of the target processing and the start of
            # waiting for the target to be processed.
            1
            +
            # Request after 0.6 seconds - processed
            1
        )
        # At the time of writing there is a bug which prevents request
        # usage from being tracked so we cannot track this.
        expected_requests = 0
        assert report.request_usage == expected_requests


def test_custom_seconds_between_requests(
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to customize the time waited between polling
    requests.
    """
    runner = CliRunner()
    with MockVWS(processing_time_seconds=0.5) as mock:
        mock_database = CloudDatabase()
        mock.add_cloud_database(cloud_database=mock_database)
        vws_client = VWS(
            server_access_key=mock_database.server_access_key,
            server_secret_key=mock_database.server_secret_key,
        )

        target_id = vws_client.add_target(
            name="x",
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )

        commands = [
            "wait-for-target-processed",
            "--target-id",
            target_id,
            "--seconds-between-requests",
            "0.3",
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert not bool(result.stdout)
        report = vws_client.get_database_summary_report()
        expected_requests = (
            # Add target request
            1
            +
            # Database summary request
            1
            +
            # Initial request
            1
            +
            # Request after 0.3 seconds - not processed
            # This assumes that there is less than 0.2 seconds taken
            # between the start of the target processing and the start of
            # waiting for the target to be processed.
            1
            +
            # Request after 0.6 seconds - processed
            1
        )
        # At the time of writing there is a bug which prevents request
        # usage from being tracked so we cannot track this.
        expected_requests = 0
        assert report.request_usage == expected_requests


def test_custom_seconds_too_small(mock_database: CloudDatabase) -> None:
    """
    The minimum valid value for ``--seconds-between-requests`` is
    0.05
    seconds.
    """
    runner = CliRunner()
    commands = [
        "wait-for-target-processed",
        "--target-id",
        "x",
        "--seconds-between-requests",
        "0.01",
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code != 0
    assert not bool(result.stdout)
    expected_substring = "0.01 is not in the range x>=0.05."
    assert expected_substring in result.stderr


def test_custom_timeout(high_quality_image: io.BytesIO) -> None:
    """It is possible to set a maximum timeout."""
    runner = CliRunner()
    with MockVWS(processing_time_seconds=0.5) as mock:
        mock_database = CloudDatabase()
        mock.add_cloud_database(cloud_database=mock_database)
        vws_client = VWS(
            server_access_key=mock_database.server_access_key,
            server_secret_key=mock_database.server_secret_key,
        )

        target_id = vws_client.add_target(
            name="x",
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )

        report = vws_client.get_target_summary_report(target_id=target_id)
        assert report.status == TargetStatuses.PROCESSING

        commands = [
            "wait-for-target-processed",
            "--target-id",
            target_id,
            "--timeout-seconds",
            "0.1",
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code != 0
        assert result.stderr == (
            "Error: The target processing time has exceeded the allowed "
            "limit.\n"
        )

        commands = [
            "wait-for-target-processed",
            "--target-id",
            target_id,
            "--timeout-seconds",
            "0.5",
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        report = vws_client.get_target_summary_report(target_id=target_id)
        assert report.status != TargetStatuses.PROCESSING


def test_custom_timeout_too_small(mock_database: CloudDatabase) -> None:
    """
    The minimum valid value for ``--timeout-seconds`` is 0.05
    seconds.
    """
    runner = CliRunner()
    commands = [
        "wait-for-target-processed",
        "--target-id",
        "x",
        "--timeout-seconds",
        "0.01",
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code != 0
    expected_substring = "0.01 is not in the range x>=0.05."
    assert expected_substring in result.stderr
