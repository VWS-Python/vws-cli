"""
Tests for how errors from VWS are handled by the CLI.
"""

import io
import uuid
from pathlib import Path

from click.testing import CliRunner
from mock_vws import MockVWS
from mock_vws.states import States
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
            expected_stderr = 'Error: Target "x/1" does not exist.\n'
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
    expected_stderr = (
        'Error: The given image is corrupted or the format is not supported.\n'
    )
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
        'Error: The request made to Vuforia was invalid and could not be '
        'processed. '
        'Check the given parameters.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_metadata_too_large(
    mock_database: VuforiaDatabase,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    An error is given when the given metadata is too large.
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
        '--application-metadata',
        'a' * 1024 * 1024 * 10,
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, args, catch_exceptions=False)
    assert result.exit_code == 1
    expected_stderr = 'Error: The given metadata is too large.\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_image_too_large(
    mock_database: VuforiaDatabase,
    png_too_large: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    An error is given when the given image is too large.
    """
    runner = CliRunner(mix_stderr=False)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = png_too_large.getvalue()
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
    assert result.exit_code == 1
    expected_stderr = 'Error: The given image is too large.\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_target_name_exist(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    An error is given when there is already a target with the given name.
    """
    name = 'foobar'
    vws_client.add_target(
        name=name,
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )

    runner = CliRunner(mix_stderr=False)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    commands = [
        'add-target',
        '--name',
        name,
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
    assert result.exit_code == 1
    expected_stderr = 'Error: There is already a target named "foobar".\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_project_inactive(
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
            'add-target',
            '--name',
            'foo',
            '--width',
            '0.1',
            '--image',
            str(new_file),
            '--server-access-key',
            database.server_access_key,
            '--server-secret-key',
            database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)

    assert result.exit_code == 1
    expected_stderr = (
        'Error: The project associated with the given keys is inactive.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''



def test_unknown_vws_error(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    XXX
    """

def test_target_status_not_success(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    XXX
    """
