"""
XXX
"""

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

def test_list_targets(_mock_database: VuforiaDatabase) -> None:
    with MockVWS() as mock:
        database = VuforiaDatabase()
        mock.add_database(database=database)
