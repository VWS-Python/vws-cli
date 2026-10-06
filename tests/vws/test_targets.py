"""Tests for `vws` targets commands."""

import io

import yaml
from click.testing import CliRunner
from mock_vws.database import CloudDatabase
from vws import VWS

from vws_cli import vws_group


def test_list_targets(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """It is possible to get a list of targets in the database."""
    runner = CliRunner()
    target_id_1 = vws_client.add_target(
        name="x1",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name="x2",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    commands = [
        "list-targets",
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
    expected_result_data = [target_id_1, target_id_2]
    # We do not expect a particular order.
    assert sorted(result_data) == sorted(expected_result_data)


def test_get_target_record(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """It is possible to get a target record."""
    runner = CliRunner()
    target_id = vws_client.add_target(
        name="x",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    commands = [
        "get-target-record",
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
        "name": "x",
        "reco_rating": "",
        "target_id": target_id,
        "tracking_rating": -1,
        "width": 1,
    }
    assert result_data == expected_result_data


def test_delete_target(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """It is possible to delete a target."""
    runner = CliRunner()
    target_id = vws_client.add_target(
        name="x",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    assert vws_client.list_targets() == [target_id]
    commands = [
        "delete-target",
        "--target-id",
        target_id,
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    vws_client.wait_for_target_processed(target_id=target_id)
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    assert not bool(result.stdout)
    assert vws_client.list_targets() == []


def test_get_duplicate_targets(
    *,
    mock_database: CloudDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """It is possible to get a list of duplicate targets."""
    runner = CliRunner()
    target_id = vws_client.add_target(
        name="x",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name="x2",
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )

    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.wait_for_target_processed(target_id=target_id_2)

    commands = [
        "get-duplicate-targets",
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
    expected_result_data = [target_id_2]
    assert result_data == expected_result_data
