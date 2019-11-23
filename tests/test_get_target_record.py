"""
XXX
"""

import io

import yaml
from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group


def test_get_target_record(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    runner = CliRunner()
    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    commands = [
        'get-target-record',
        '--target-id',
        target_id,
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    result_data = yaml.load(result.stdout, Loader=yaml.FullLoader)
    expected_result_data = {
        'active_flag': True,
        'name': 'x',
        'reco_rating': '',
        'target_id': target_id,
        'tracking_rating': -1,
        'width': 1,
    }
    assert result_data == expected_result_data
