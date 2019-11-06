"""
XXX
"""

import pytest
from typing import Iterator
from textwrap import dedent

from click.testing import CliRunner
import io
from vws_cli import vws_group

from mock_vws import MockVWS
from vws import VWS
from mock_vws.database import VuforiaDatabase


@pytest.fixture()
def mock_database() -> Iterator[VuforiaDatabase]:
    """
    Yield a mock ``VuforiaDatabase``.
    """
    with MockVWS() as mock:
        database = VuforiaDatabase()
        mock.add_database(database=database)
        yield database

@pytest.fixture()
def vws_client(mock_database: VuforiaDatabase) -> Iterator[VWS]:
    """
    Yield a VWS client which connects to a mock database.
    """
    yield VWS(
        server_access_key=mock_database.server_access_key,
        server_secret_key=mock_database.server_secret_key,
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
