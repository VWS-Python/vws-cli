"""
Tests for how errors from VWS are handled by the CLI.
"""

import io
import uuid
from pathlib import Path

from click.testing import CliRunner
from freezegun import freeze_time
from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase
from mock_vws.states import States
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
                'abc12345',
                '--server-access-key',
                mock_database.server_access_key,
                '--server-secret-key',
                mock_database.server_secret_key,
            ]
            result = runner.invoke(vws_group, args, catch_exceptions=False)
            assert result.exit_code == 1
            expected_stderr = 'Error: Target "abc12345" does not exist.\n'
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
    high_quality_image: io.BytesIO,
    tmp_path: Path,
) -> None:
    """
    When an unknown VWS error is given, e.g. what is given when some bad names
    are given, an error is given.
    """
    runner = CliRunner(mix_stderr=False)
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    max_char_value = 65535
    bad_name = chr(max_char_value + 1)

    commands = [
        'add-target',
        '--name',
        bad_name,
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
    expected_stderr = (
        'Error: There was an unknown error from Vuforia. '
        'This may be because there is a problem with the given name.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_target_status_processing(
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    mock_database: VuforiaDatabase,
) -> None:
    """
    An error is given when trying to delete a target which is processing.
    """
    runner = CliRunner(mix_stderr=False)

    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )

    commands = [
        'delete-target',
        '--target-id',
        target_id,
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]

    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 1
    expected_stderr = (
        f'Error: The target "{target_id}" cannot be deleted as it is in the '
        'processing state.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_target_status_not_success(
    vws_client: VWS,
    high_quality_image: io.BytesIO,
    mock_database: VuforiaDatabase,
) -> None:
    """
    An error is given when updating a target which has a status
    which is not "Success".
    """
    runner = CliRunner(mix_stderr=False)
    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )

    commands = [
        'update-target',
        '--target-id',
        target_id,
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]

    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 1
    expected_stderr = (
        f'Error: The target "{target_id}" cannot be updated as it is in the '
        'processing state.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_authentication_failure(mock_database: VuforiaDatabase) -> None:
    """
    An error is given when the secret key is incorrect.
    """
    runner = CliRunner(mix_stderr=False)
    commands = [
        'list-targets',
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        'wrong_key',
    ]

    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 1
    expected_stderr = 'The given secret key was incorrect.\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''


def test_request_time_too_skewed(mock_database: VuforiaDatabase) -> None:
    """
    An error is given when the request time is more than 5 minutes different
    from the server time.
    """
    runner = CliRunner(mix_stderr=False)
    vws_max_time_skew = 60 * 5
    leeway = 10
    time_difference_from_now = vws_max_time_skew + leeway

    # We use a custom tick because we expect the following:
    #
    # * At least one time check when creating the request
    # * At least one time check when processing the request
    #
    # >= 1 ticks are acceptable.
    with freeze_time(auto_tick_seconds=time_difference_from_now):
        commands = [
            'list-targets',
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)

    expected_stderr = (
        'Error: Vuforia reported that the time given with this request was '
        'outside the expected range. '
        'This may be because the system clock is out of sync.\n'
    )
    assert result.stderr == expected_stderr
    assert result.stdout == ''
