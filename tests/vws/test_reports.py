"""Tests for `vws` reports commands."""

import io

import yaml
from click.testing import CliRunner
from freezegun import freeze_time
from mock_vws.database import CloudDatabase
from vws import VWS

from vws_cli import vws_group


def test_get_database_summary_report(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """It is possible to get a database summary report."""
    runner = CliRunner()
    for name in ("a", "b"):
        _ = vws_client.add_target(
            name=name,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )

    commands = [
        "get-database-summary-report",
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
    result_data = yaml.safe_load(stream=result.stdout)
    expected_result_data = {
        "active_images": 0,
        "current_month_recos": 0,
        "failed_images": 0,
        "inactive_images": 0,
        "name": mock_database.database_name,
        "previous_month_recos": 0,
        "processing_images": 2,
        "reco_threshold": 1000,
        "request_quota": 100000,
        "request_usage": 0,
        "target_quota": 1000,
        "total_recos": 0,
    }
    assert result_data == expected_result_data


def test_get_target_summary_report(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """It is possible to get a target summary report."""
    runner = CliRunner()
    upload_date = "2015-04-29"
    with freeze_time(time_to_freeze=upload_date):
        target_id = vws_client.add_target(
            name="x",
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )

    commands = [
        "get-target-summary-report",
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
    result_data = yaml.safe_load(stream=result.stdout)
    expected_result_data = {
        "active_flag": True,
        "current_month_recos": 0,
        "database_name": mock_database.database_name,
        "previous_month_recos": 0,
        "status": "success",
        "target_name": "x",
        "total_recos": 0,
        "tracking_rating": result_data["tracking_rating"],
        "upload_date": upload_date,
    }
    assert result_data == expected_result_data
