"""
XXX
"""

import io

import yaml
from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group


def test_get_target_summary_report(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    runner = CliRunner()
    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
    )
    commands = [
        'get-target-summary-report',
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
        'current_month_recos': 0,
        'database_name': mock_database.database_name,
        'previous_month_recos': 0,
        'result_code': 'Success',
        'status': 'processing',
        'target_name': 'x',
        'total_recos': 0,
        'tracking_rating': -1,
        'transaction_id': result_data['transaction_id'],
        'upload_date': result_data['upload_date'],
    }
    assert result_data == expected_result_data


def test_target_does_not_exist(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
) -> None:
    runner = CliRunner(mix_stderr=False)
    commands = [
        'get-target-summary-report',
        '--target-id',
        'x',
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 1
    expected_stderr = 'Target "x" does not exist.\n'
    assert result.stderr == expected_stderr
    assert result.stdout == ''

