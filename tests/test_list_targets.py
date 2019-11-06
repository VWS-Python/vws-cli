"""
XXX
"""

from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase

def test_list_targets():
    with MockVWS() as mock:
        database = VuforiaDatabase()
        mock.add_database(database=database)

    pass
