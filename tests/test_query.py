"""
Test for the Cloud Reco Service commands.
"""

import io
import uuid
from pathlib import Path

from click.testing import CliRunner

from vws_cli.query import vuforia_cloud_reco


class TestQuery:
    """
    Tests for making image queries.
    """

    def test_no_matches(
        self,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """
        An empty list is returned if there are no matches.
        """
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
        assert result.stdout == ''

    def test_image_file_is_dir():
        pass

    def test_relative_path():
        pass

    def test_matches():
        pass
