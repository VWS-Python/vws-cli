"""
Tests for how errors from the Cloud Reco Service are handled by the CLI.
"""

import io
import uuid
from pathlib import Path
from typing import List

from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
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
    commands: List[str] = [
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
    commands: List[str] = [
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


def test_match_processing(
    mock_database: VuforiaDatabase,
    tmp_path: Path,
    high_quality_image: io.BytesIO,
    vws_client: VWS,
) -> None:
    """
    An error is given when the image matches a target which is processing.
    """
    runner = CliRunner(mix_stderr=False)
    vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    commands: List[str] = [
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
        'Error: The given image matches a target which was recently added, '
        'updated or deleted and Vuforia returns an error in this case.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''
