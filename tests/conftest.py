"""``pytest`` fixtures."""

from collections.abc import Iterator

import pytest
from beartype import beartype
from mock_vws import MockVWS
from mock_vws.database import CloudDatabase, VuMarkDatabase
from mock_vws.target import VuMarkTarget
from vws import VWS, CloudRecoService


@beartype
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply the beartype decorator to all collected test functions."""
    for item in items:
        assert isinstance(item, pytest.Function)
        item.obj = beartype(obj=item.obj)


@pytest.fixture(name="mock_database")
def fixture_mock_database() -> Iterator[CloudDatabase]:
    """Yield a mock ``CloudDatabase``."""
    with MockVWS() as mock:
        database = CloudDatabase()
        mock.add_cloud_database(cloud_database=database)
        yield database


@pytest.fixture
def vws_client(*, mock_database: CloudDatabase) -> VWS:
    """Return a VWS client which connects to a mock database."""
    return VWS(
        server_access_key=mock_database.server_access_key,
        server_secret_key=mock_database.server_secret_key,
    )


@pytest.fixture(name="vumark_database")
def fixture_vumark_database() -> Iterator[VuMarkDatabase]:
    """Yield a mock ``VuMarkDatabase`` with one pre-created target."""
    vumark_target = VuMarkTarget(name="test-vumark-target")
    database = VuMarkDatabase(vumark_targets={vumark_target})
    with MockVWS() as mock:
        mock.add_vumark_database(vumark_database=database)
        yield database


@pytest.fixture(name="vumark_target")
def fixture_vumark_target(vumark_database: VuMarkDatabase) -> VuMarkTarget:
    """Return the pre-created ``VuMarkTarget`` in the database."""
    return next(iter(vumark_database.not_deleted_targets))


@pytest.fixture
def cloud_reco_client(
    *,
    mock_database: CloudDatabase,
) -> CloudRecoService:
    """
    Return a ``CloudRecoService`` client which connects to a mock
    database.
    """
    return CloudRecoService(
        client_access_key=mock_database.client_access_key,
        client_secret_key=mock_database.client_secret_key,
    )
