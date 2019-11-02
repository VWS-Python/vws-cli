"""
Tests for the VWS CLI.
"""

from vws_cli import vws
from click.testing import CliRunner

def test_version():
    """
    The CLI version is shown with ``minidcos --version``.
    """
    runner = CliRunner()
    result = runner.invoke(
        vws,
        ['--version'],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    expected = 'vws, version'
    assert expected in result.stdout
