"""
Test for the Cloud Reco Service commands.
"""

import io
import uuid
from pathlib import Path

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
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        An empty list is returned if there are no matches.
        """
        runner = CliRunner(mix_stderr=False)
        commands = []
        result = runner.invoke(
            vuforia_cloud_reco,
            commands,
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert result.stdout == ''

