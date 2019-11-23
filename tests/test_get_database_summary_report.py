"""
XXX
"""

import io

import yaml
from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group


def test_get_database_summary_report(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    runner = CliRunner()
    for name in ('a', 'b'):
        vws_client.add_target(
            name=name,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )

    commands = [
        'get-database-summary-report',
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    result_data = yaml.load(result.stdout, Loader=yaml.FullLoader)
    expected_result_data = {
        'active_images': 0,
        'current_month_recos': 0,
        'failed_images': 0,
        'inactive_images': 0,
        'name': mock_database.database_name,
        'previous_month_recos': 0,
        'processing_images': 2,
        'reco_threshold': 1000,
        'request_quota': 100000,
        'request_usage': 0,
        'result_code': 'Success',
        'target_quota': 1000,
        'total_recos': 0,
        'transaction_id': result_data['transaction_id'],
    }
    assert result_data == expected_result_data
