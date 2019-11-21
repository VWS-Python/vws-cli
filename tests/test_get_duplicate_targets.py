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
    target_id_2 = vws_client.add_target(
        name='x2',
        width=1,
        image=high_quality_image,
    )

    vws_client.wait_for_target_processed(target_id)
    vws_client.wait_for_target_processed(target_id_2)

    commands = [
        'get-duplicate-targets',
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
    expected_result_data = [target_id_2]
    assert result_data == expected_result_data


def test_target_does_not_exist(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
) -> None:
    runner = CliRunner(mix_stderr=False)
    commands = [
        'get-duplicate-targets',
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

