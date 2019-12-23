"""
Test for the Cloud Reco Service commands.
"""

import io
import uuid
from pathlib import Path
from textwrap import dedent
from typing import List

import yaml
from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase

from vws_cli.query import vuforia_cloud_reco


class TestQuery:
    """
    Tests for making image queries.
    """

    def test_no_matches(
        self,
        mock_database: VuforiaDatabase,
        tmp_path: Path,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        An empty list is returned if there are no matches.
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
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            vuforia_cloud_reco,
            commands,
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert result.stdout == ''


    def test_matches(
        self,
        tmp_path: Path,
        high_quality_image: io.BytesIO,
        mock_database: VuforiaDatabase,
    ) -> None:
        runner = CliRunner(mix_stderr=False)
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
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
        assert result.exit_code == 0
        result_data = yaml.load(result.stdout, Loader=yaml.FullLoader)
        expected_result_data = {}
        assert result_data == expected_result_data

    def test_image_file_is_dir(
        self,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        An appropriate error is given if the given image file path points to a
        directory.
        """
        runner = CliRunner(mix_stderr=False)
        commands: List[str] = [
            str(tmp_path),
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
        assert result.exit_code == 2
        assert result.stdout == ''
        expected_stderr = dedent(
            f"""\
            Usage: vuforia-cloud-reco [OPTIONS] IMAGE
            Try "vuforia-cloud-reco --help" for help.

            Error: Invalid value for "IMAGE": File "{tmp_path}" is a directory.
            """,  # noqa: E501
        )
        assert result.stderr == expected_stderr

    def test_relative_path(
        self,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        Image file paths are resolved.
        """
        runner = CliRunner(mix_stderr=False)
        new_filename = uuid.uuid4().hex
        original_image_file = tmp_path / 'foo'
        image_data = high_quality_image.getvalue()
        original_image_file.write_bytes(image_data)
        commands: List[str] = [
            str(new_filename),
            '--client-access-key',
            mock_database.client_access_key,
            '--client-secret-key',
            mock_database.client_secret_key,
        ]
        with runner.isolated_filesystem():
            new_file = Path(new_filename)
            new_file.symlink_to(original_image_file)
            result = runner.invoke(
                vuforia_cloud_reco,
                commands,
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert result.stdout == ''

    def test_image_file_does_not_exist(
        self,
        mock_database: VuforiaDatabase,
        tmp_path: Path,
    ) -> None:
        """
        An appropriate error is given if the given image file does not exist.
        """
        runner = CliRunner(mix_stderr=False)
        does_not_exist_file = tmp_path / uuid.uuid4().hex
        commands: List[str] = [
            str(does_not_exist_file),
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
        assert result.exit_code == 2
        assert result.stdout == ''
        expected_stderr = dedent(
            f"""\
            Usage: vuforia-cloud-reco [OPTIONS] IMAGE
            Try "vuforia-cloud-reco --help" for help.

            Error: Invalid value for "IMAGE": File "{does_not_exist_file}" does not exist.
            """,  # noqa: E501
        )
        assert result.stderr == expected_stderr


def test_version() -> None:
    """
    ``vuforia-cloud-reco --version`` shows the version.
    """
    runner = CliRunner(mix_stderr=False)
    commands = ['--version']
    result = runner.invoke(
        vuforia_cloud_reco,
        commands,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert result.stdout.startswith('vuforia-cloud-reco, version ')
