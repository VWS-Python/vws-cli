"""
XXX
"""

import pytest
from typing import Iterator

from click.testing import CliRunner
import io
from vws_cli import vws_group

from mock_vws import MockVWS
from vws import VWS
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

@pytest.fixture()
def vws_client(_mock_database: VuforiaDatabase) -> Iterator[VWS]:
    """
    Yield a VWS client which connects to a mock database.
    """
    yield VWS(
        server_access_key=_mock_database.server_access_key,
        server_secret_key=_mock_database.server_secret_key,
    )

@pytest.fixture()
def high_quality_image() -> io.BytesIO:
    """
    Return an image file which is expected to have a 'success' status when
    added to a target and a high tracking rating.

    At the time of writing, this image gains a tracking rating of 5.
    """
    path = 'tests/data/high_quality_image.jpg'
    with open(path, 'rb') as high_quality_image_file:
        return io.BytesIO(high_quality_image_file.read())

# TODO list targets after adding a target
# TODO use credentials file?
# TODO generic auth error test (secret and client keys)
# TODO generic request time too skewed test

def test_list_targets(
    _mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    runner = CliRunner()
    target_id_1 = vws_client.add_target(
        name='x1',
        width=1,
        image=high_quality_image,
    )
    target_id_2 = vws_client.add_target(
        name='x2',
        width=1,
        image=high_quality_image,
    )
    commands = [
        'list-targets',
        '--server-access-key',
        _mock_database.server_access_key,
        '--server-secret-key',
        _mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    expected = dedent(
        f'{target_id_1}',
        f'{target_id_2}',
    )
    assert result.stdout == expected
