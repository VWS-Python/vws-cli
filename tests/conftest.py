"""
``pytest`` fixtures.
"""

from typing import Iterator

import pytest
from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase
from vws import VWS, CloudRecoService


@pytest.fixture(name='mock_database')
def fixture_mock_database() -> Iterator[VuforiaDatabase]:
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
def cloud_reco_client(
    mock_database: VuforiaDatabase,
) -> Iterator[CloudRecoService]:
    """
    Yield a ``CloudRecoService`` client which connects to a mock database.
    """
    yield CloudRecoService(
        client_access_key=mock_database.client_access_key,
        client_secret_key=mock_database.client_secret_key,
    )
