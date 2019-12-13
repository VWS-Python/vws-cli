"""
Tests for how errors from VWS are handled by the CLI.
"""

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
    vws_client: VWS,
    tmp_path: Path,
) -> None:
    """
    An error is given when a corrupt image is uploaded.
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
