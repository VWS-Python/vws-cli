"""
Tests for the VWS CLI.
"""

import click

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
    expected = 'minidcos, version'
    assert expected in result.output
