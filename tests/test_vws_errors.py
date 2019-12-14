"""
Tests for how errors from VWS are handled by the CLI.
"""

import io
import uuid
from pathlib import Path

from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group


def test_target_id_does_not_exist(mock_database: VuforiaDatabase) -> None:
    """
    Commands which take a target ID show an error if that does not map to a
    target in the database.
    """
    runner = CliRunner(mix_stderr=False)
    for command_name, command in vws_group.commands.items():
        if 'target_id' in [option.name for option in command.params]:
            args = [
                command_name,
                '--target-id',
                'x/1',
                '--server-access-key',
                mock_database.server_access_key,
                '--server-secret-key',
                mock_database.server_secret_key,
            ]
            result = runner.invoke(vws_group, args, catch_exceptions=False)
            assert result.exit_code == 1
            expected_stderr = 'Target "x/1" does not exist.\n'
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
    args = [
        'add-target',
        '--name',
        'x',
        '--width',
        '0.1',
        '--image',
        str(new_file),
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, args, catch_exceptions=False)
    assert result.exit_code == 1
    expected_stderr = 'Image corrupted or format not supported.\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_fail_bad_request(
    mock_database: VuforiaDatabase,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    An error is given when Vuforia returns a ``Fail`` error with a ``400``
    error code. For example, when the given server access key does not exist.

    With ``vws_python`` we cannot get a (guaranteed) 500 error or 422 response
    with a ``Fail`` error.
    """
    new_file = tmp_path / uuid.uuid4().hex
    new_file.write_bytes(data=high_quality_image.getvalue())
    runner = CliRunner(mix_stderr=False)
    args = [
        'add-target',
        '--name',
        'x',
        '--width',
        '0.1',
        '--image',
        str(new_file),
        '--server-access-key',
        'does_not_exist_key',
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, args, catch_exceptions=False)
    assert result.exit_code == 1
    expected_stderr = (
        'The request was invalid and could not be processed. Check the '
        'request headers and fields.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_metadata_too_large(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    XXX
    """


def test_image_too_large(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    png_too_large: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    XXX
    """
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    commands = [
        'add-target',
        '--name',
        'foo',
        '--width',
        '0.1',
        '--image',
        str(new_file),
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0


def test_target_name_exist(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    XXX
    """


def test_project_inactive(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    XXX
    """


def test_unknown_vws_error(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    XXX
    """
