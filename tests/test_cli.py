"""
Tests for the VWS CLI.
"""

from vws_cli import vws_group
from click.testing import CliRunner

def test_version():
    """
    The CLI version is shown with ``vws--version``.
    """
    runner = CliRunner()
    result = runner.invoke(
        vws_group,
        ['--version'],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    expected = 'vws, version'
    assert expected in result.stdout
