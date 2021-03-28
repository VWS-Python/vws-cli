"""
Tests for how errors from the Cloud Reco Service are handled by the CLI.
"""

from __future__ import annotations

import io
import time
import uuid
from pathlib import Path

from click.testing import CliRunner
from freezegun import freeze_time
from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase
from mock_vws.states import States
from vws import VWS

from vws_cli.query import vuforia_cloud_reco


def test_authentication_failure(
    mock_database: VuforiaDatabase,
    tmp_path: Path,
    high_quality_image: io.BytesIO,
) -> None:
    """
    An error is given when the secret key is incorrect.
    """
    runner = CliRunner(mix_stderr=False)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    commands: list[str] = [
        str(new_file),
        '--client-access-key',
        mock_database.client_access_key,
        '--client-secret-key',
        'wrong_secret_key',
    ]
    result = runner.invoke(
        vuforia_cloud_reco,
        commands,
        catch_exceptions=False,
    )
    expected_stderr = 'The given secret key was incorrect.\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_image_too_large(
    mock_database: VuforiaDatabase,
    tmp_path: Path,
    png_too_large: io.BytesIO,
) -> None:
    """
    An error is given when the image is too large.
    """
    runner = CliRunner(mix_stderr=False)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = png_too_large.getvalue()
    new_file.write_bytes(data=image_data)
    commands: list[str] = [
        str(new_file),
        '--client-access-key',
        mock_database.client_access_key,
        '--client-secret-key',
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        vuforia_cloud_reco,
        commands,
        catch_exceptions=False,
    )
    expected_stderr = 'Error: The given image is too large.\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_active_matching_targets_delete_processing(
    mock_database: VuforiaDatabase,
    tmp_path: Path,
    high_quality_image: io.BytesIO,
    vws_client: VWS,
) -> None:
    """
    An error is given when the image matches a target which has recently been
    deleted.
    """
    runner = CliRunner(mix_stderr=False)

    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    vws_client.wait_for_target_processed(target_id=target_id)
    vws_client.delete_target(target_id=target_id)
    time.sleep(0.2)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    commands: list[str] = [
        str(new_file),
        '--client-access-key',
        mock_database.client_access_key,
        '--client-secret-key',
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        vuforia_cloud_reco,
        commands,
        catch_exceptions=False,
    )
    expected_stderr = (
        'Error: The given image matches a target which was recently deleted.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_bad_image(
    mock_database: VuforiaDatabase,
    tmp_path: Path,
) -> None:
    """
    An error is given when Vuforia returns a ``BadImage`` error. For example,
    when a corrupt image is uploaded.
    """
    new_file = tmp_path / uuid.uuid4().hex
    new_file.write_bytes(data=b'Not an image')
    runner = CliRunner(mix_stderr=False)
    commands: list[str] = [
        str(new_file),
        '--client-access-key',
        mock_database.client_access_key,
        '--client-secret-key',
        mock_database.client_secret_key,
    ]
    result = runner.invoke(
        vuforia_cloud_reco,
        commands,
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    expected_stderr = (
        'Error: The given image is corrupted or the format is not supported.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_inactive_project(
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    An error is given if the project is inactive and the desired action cannot
    be taken because of this.
    """
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    database = VuforiaDatabase(state=States.PROJECT_INACTIVE)
    with MockVWS() as mock:
        mock.add_database(database=database)
        runner = CliRunner(mix_stderr=False)
        commands = [
            str(new_file),
            '--client-access-key',
            database.client_access_key,
            '--client-secret-key',
            database.client_secret_key,
        ]
        result = runner.invoke(
            vuforia_cloud_reco,
            commands,
            catch_exceptions=False,
        )

    assert result.exit_code == 1
    expected_stderr = (
        'Error: The project associated with the given keys is inactive.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_request_time_too_skewed(
    high_quality_image: io.BytesIO,
    mock_database: VuforiaDatabase,
    tmp_path: Path,
) -> None:
    """
    An error is given when the request time is more than 65 minutes different
    from the server time.
    """
    runner = CliRunner(mix_stderr=False)
    vwq_max_time_skew = 60 * 65
    leeway = 10
    time_difference_from_now = vwq_max_time_skew + leeway
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)

    # We use a custom tick because we expect the following:
    #
    # * At least one time check when creating the request
    # * At least one time check when processing the request
    #
    # >= 1 ticks are acceptable.
    with freeze_time(auto_tick_seconds=time_difference_from_now):
        commands = [
            str(new_file),
            '--client-access-key',
            mock_database.client_access_key,
            '--client-secret-key',
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            vuforia_cloud_reco,
            commands,
            catch_exceptions=False,
        )

    expected_stderr = (
        'Error: Vuforia reported that the time given with this request was '
        'outside the expected range. '
        'This may be because the system clock is out of sync.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''
