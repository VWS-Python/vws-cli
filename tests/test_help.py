"""Tests for the VWS CLI help."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from click.testing import CliRunner
from vws_cli import vws_group
from vws_cli.query import vuforia_cloud_reco

if TYPE_CHECKING:
    from pytest_regressions.file_regression import FileRegressionFixture

_SUBCOMMANDS = [[item] for item in vws_group.commands]
_BASE_COMMAND: list[list[str]] = [[]]
_COMMANDS = _BASE_COMMAND + _SUBCOMMANDS


@pytest.mark.parametrize(
    "command",
    _COMMANDS,
    ids=[str(cmd) for cmd in _COMMANDS],
)
def test_vws_command_help(
    command: list[str],
    file_regression: FileRegressionFixture,
) -> None:
    """Expected help text is shown for ``vws`` commands.

    This help text is defined in files.
    To update these files, run ``pytest`` with the ``--regen-all`` flag.
    """
    runner = CliRunner()
    arguments = [*command, "--help"]
    result = runner.invoke(vws_group, arguments, catch_exceptions=False)
    assert result.exit_code == 0
    file_regression.check(contents=result.output)


def test_query_help(file_regression: FileRegressionFixture) -> None:
    """Expected help text is shown for the ``vuforia-cloud-reco`` command.

    This help text is defined in files.
    To update these files, run ``pytest`` with the ``--regen-all`` flag.
    """
    runner = CliRunner()
    arguments = ["--help"]
    result = runner.invoke(
        vuforia_cloud_reco,
        arguments,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    file_regression.check(contents=result.output)
