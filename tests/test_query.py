"""
Test for the Cloud Reco Service commands.
"""

from typing import List

from click.testing import CliRunner

from vws_cli.query import vuforia_cloud_reco


class TestQuery:
    """
    Tests for making image queries.
    """

    def test_no_matches(self) -> None:
        """
        The cloud recognition command exists.
        """
        runner = CliRunner(mix_stderr=False)
        commands: List[str] = []
        result = runner.invoke(
            vuforia_cloud_reco,
            commands,
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert result.stdout == ''
