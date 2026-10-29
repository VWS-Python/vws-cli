"""``pytest`` fixtures."""

from collections.abc import Iterator

import pytest
from mock_vws import MockVWS
from mock_vws.database import VuMarkDatabase
from mock_vws.target import VuMarkTarget


@pytest.fixture(name="vumark_database")
def fixture_vumark_database() -> Iterator[VuMarkDatabase]:
    """Yield a mock ``VuMarkDatabase`` with one pre-created target."""
    vumark_target = VuMarkTarget(name="test-vumark-target")
    database = VuMarkDatabase(vumark_targets={vumark_target})
    with MockVWS() as mock:
        mock.add_vumark_database(vumark_database=database)
        yield database


@pytest.fixture(name="vumark_target")
def fixture_vumark_target(*, vumark_database: VuMarkDatabase) -> VuMarkTarget:
    """Return the pre-created ``VuMarkTarget`` in the database."""
    return next(iter(vumark_database.not_deleted_targets))
