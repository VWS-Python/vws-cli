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

# TODO list targets empty
# TODO list targets after adding a target
# TODO use credentials file?
# TODO generic auth error test

def test_list_targets(_mock_database: VuforiaDatabase) -> None:
    runner = CliRunner()
    commands = [
        'list-targets',
        '--client-access-key',
        client_access_key]
    result = runner.invoke(
        vws_group,
        ['--version'],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    expected = 'vws, version'
    assert expected in result.stdout
