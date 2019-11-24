"""
Tests for VWS CLI commands.
"""

import io
from textwrap import dedent

import yaml
from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group


def test_target_id_does_not_exist(mock_database: VuforiaDatabase) -> None:
    """
    Commands which take a target ID show an error if that does not map to a
    target in the database.
    """
    runner = CliRunner(mix_stderr=False)
    for command_name, command in vws_group.commands.items():
        if 'target_id' in [option.name for option in command.params]:
            args = [
                command_name,
                '--target-id',
                'x/1',
                '--server-access-key',
                mock_database.server_access_key,
                '--server-secret-key',
                mock_database.server_secret_key,
            ]
            result = runner.invoke(vws_group, args, catch_exceptions=False)
            assert result.exit_code == 1
            expected_stderr = 'Target "x/1" does not exist.\n'
            assert result.stderr == expected_stderr
            assert result.stdout == ''


def test_get_database_summary_report(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to get a database summary report.
    """
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


def test_list_targets(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to get a list of targets in the database.
    """
    runner = CliRunner()
    target_id_1 = vws_client.add_target(
        name='x1',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name='x2',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    commands = [
        'list-targets',
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    expected = dedent(
        f"""\
        {target_id_1}
        {target_id_2}
        """,
    )
    assert result.stdout == expected


def test_get_target_record(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to get a target record.
    """
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


def test_get_target_summary_report(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to get a target summary report.
    """
    runner = CliRunner()
    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
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


def test_delete_target(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to delete a target.
    """
    runner = CliRunner()
    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    assert vws_client.list_targets() == [target_id]
    commands = [
        'delete-target',
        '--target-id',
        target_id,
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
    ]
    vws_client.wait_for_target_processed(target_id=target_id)
    result = runner.invoke(vws_group, commands, catch_exceptions=False)
    assert result.exit_code == 0
    assert result.stdout == ''
    assert vws_client.list_targets() == []


def test_get_duplicate_targets(
    mock_database: VuforiaDatabase,
    vws_client: VWS,
    high_quality_image: io.BytesIO,
) -> None:
    """
    It is possible to get a list of duplicate targets.
    """
    runner = CliRunner()
    target_id = vws_client.add_target(
        name='x',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
    )
    target_id_2 = vws_client.add_target(
        name='x2',
        width=1,
        image=high_quality_image,
        active_flag=True,
        application_metadata=None,
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

class TestWaitForTargetProcessed:

    def test_wait_for_target_processed(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        target_id = vws_client.add_target(
            name='x',
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
