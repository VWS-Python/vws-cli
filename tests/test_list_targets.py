"""
XXX
"""

import pytest
from typing import Iterator

from click.testing import CliRunner
from vws_cli import vws_group

from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase

@pytest.fixture()
def _mock_database() -> Iterator[VuforiaDatabase]:
    """
    Yield a mock ``VuforiaDatabase``.
    """
    with MockVWS() as mock:
        database = VuforiaDatabase()
        mock.add_database(database=database)
        yield database

# TODO list targets after adding a target
# TODO use credentials file?
# TODO generic auth error test

def test_list_targets(_mock_database: VuforiaDatabase) -> None:
    runner = CliRunner()
    commands = [
        'list-targets',
        '--client-access-key',
        _mock_database.client_access_key,
        '--client-secret-key',
        _mock_database.client_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    expected = ''
    assert result.stdout == expected
