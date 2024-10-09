"""``pytest`` fixtures."""

from collections.abc import Iterator

import pytest
from beartype import beartype
from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase
from vws import VWS, CloudRecoService


@beartype
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Apply the beartype decorator to all collected test functions.
    """
    for item in items:
        assert isinstance(item, pytest.Function)
        item.obj = beartype(obj=item.obj)


@beartype
@pytest.fixture(name="mock_database")
def fixture_mock_database() -> Iterator[VuforiaDatabase]:
    """Yield a mock ``VuforiaDatabase``."""
    with MockVWS() as mock:
        database = VuforiaDatabase()
        mock.add_database(database=database)
        yield database


@beartype
@pytest.fixture
def vws_client(mock_database: VuforiaDatabase) -> VWS:
    """Return a VWS client which connects to a mock database."""
    return VWS(
        server_access_key=mock_database.server_access_key,
        server_secret_key=mock_database.server_secret_key,
    )


@pytest.fixture
def cloud_reco_client(
    mock_database: VuforiaDatabase,
) -> CloudRecoService:
    """Return a ``CloudRecoService`` client which connects to a mock database."""
    return CloudRecoService(
        client_access_key=mock_database.client_access_key,
        client_secret_key=mock_database.client_secret_key,
    )
