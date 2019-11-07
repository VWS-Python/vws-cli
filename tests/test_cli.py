"""
Tests for the VWS CLI.
"""

from click.testing import CliRunner

from vws_cli import vws_group


def test_version() -> None:
    """
    The CLI version is shown with ``vws --version``.
    """
    runner = CliRunner()
    result = runner.invoke(vws_group, ['--version'], catch_exceptions=False)
    assert result.exit_code == 0
    expected = 'vws, version'
    assert expected in result.stdout
