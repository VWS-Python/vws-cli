"""
Test for the Cloud Reco Service commands.
"""

<<<<<<< HEAD
import io
import uuid
from pathlib import Path

import yaml
from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
=======
from typing import List

from click.testing import CliRunner
>>>>>>> master

from vws_cli.query import vuforia_cloud_reco


class TestQuery:
    """
    Tests for making image queries.
    """

<<<<<<< HEAD
    def test_no_matches(
        self,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        An empty list is returned if there are no matches.
        """
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
=======
    def test_no_matches(self) -> None:
        """
        The cloud recognition command exists.
        """
        runner = CliRunner(mix_stderr=False)
        commands: List[str] = []
>>>>>>> master
        result = runner.invoke(
            vuforia_cloud_reco,
            commands,
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert result.stdout == ''
<<<<<<< HEAD

    def test_image_file_is_dir(self):
        pass

    def test_relative_path(self):
        pass

    def test_matches(
        self,
        tmp_path: Path,
        high_quality_image: io.BytesIO
    ) -> None:
        runner = CliRunner(mix_stderr=False)
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [str(new_file)]
        result = runner.invoke(
            vuforia_cloud_reco,
            commands,
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        result_data = yaml.load(result.stdout, Loader=yaml.FullLoader)
        expected_result_data = {}
        assert result_data == expected_result_data
=======
>>>>>>> master
