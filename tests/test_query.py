"""
Test for the Cloud Reco Service commands.
"""

import uuid
from pathlib import Path
from typing import List

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
    ) -> None:
        """
        The cloud recognition command exists.
        """
        runner = CliRunner(mix_stderr=False)
        file_path = tmp_path / uuid.uuid4().hex
        file_path.touch()
        commands: List[str] = [
            str(file_path),
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
