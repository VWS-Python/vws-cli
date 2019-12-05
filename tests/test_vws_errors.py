"""
Tests for how errors from VWS are handled by the CLI.
"""

import io

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
    self,
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    pass


def test_fail(
    self,
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    pass


def test_metadata_too_large(
    self,
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    pass


def test_image_too_large(
    self,
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    pass


def test_target_name_exist(
    self,
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    pass


def test_project_inactive(
    self,
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    pass


def test_unknown_vws_error(
    self,
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    pass
