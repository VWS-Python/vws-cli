"""
XXX
"""

import pytest
import yaml
from typing import Iterator
from textwrap import dedent

from click.testing import CliRunner
import io
from vws_cli import vws_group

from mock_vws import MockVWS
from vws import VWS
from mock_vws.database import VuforiaDatabase


# TODO use credentials file?
# TODO generic auth error test (secret and client keys)
# TODO generic request time too skewed test

def test_get_database_summary_report(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    runner = CliRunner()
    target_id_1 = vws_client.add_target(
        name='x1',
        width=1,
        image=high_quality_image,
    )
    target_id_2 = vws_client.add_target(
        name='x2',
        width=1,
        image=high_quality_image,
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
