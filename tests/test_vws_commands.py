"""
Tests for VWS CLI commands.
"""

import io
import uuid
import random
from pathlib import Path
from textwrap import dedent

import yaml
from click.testing import CliRunner
from mock_vws import MockVWS
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


class TestAddTarget:
    """
    Tests for ``vws add-target``.
    """

    # TODO test give file does not exist, give dir which does exist, give relative path

    def test_add_target(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        name = uuid.uuid4().hex
        new_file.write_bytes(data=high_quality_image.read())
        width = random.uniform(a=0.01, b=50)
        commands = [
            'add-target',
            '--name',
            name,
            '--width',
            width,
            '--image',
            str(new_file),
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 0

        target_id = result.stdout.strip()
        target_record = vws_client.get_target_record(target_id=target_id)
        assert target_record['name'] == name
        assert target_record['width'] == width
        assert target_record['active_flag'] == True
        # TODO make a query so we can see that the metadata is None
        # TODO make a query so we can see that the image has been uploaded
        #   fine.


    def test_custom_metadata(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_custom_active_flag(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_bad_image(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_fail(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_metadata_too_large(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_image_too_large(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_target_name_exist(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_project_inactive(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass

    def test_unknown_vws_error(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        pass


class TestWaitForTargetProcessed:
    """
    Tests for ``vws wait-for-target-processed``.
    """

    def test_wait_for_target_processed(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        It is possible to use a command to wait for a target to be processed.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name='x',
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        report = vws_client.get_target_summary_report(target_id=target_id)
        assert report['status'] == 'processing'
        commands = [
            'wait-for-target-processed',
            '--target-id',
            target_id,
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 0
        assert result.stdout == ''
        report = vws_client.get_target_summary_report(target_id=target_id)
        assert report['status'] != 'processing'

    def test_default_seconds_between_requests(
        self,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        By default, 0.2 seconds are waited between polling requests.
        """
        runner = CliRunner()
        with MockVWS(processing_time_seconds=0.5) as mock:
            mock_database = VuforiaDatabase()
            mock.add_database(database=mock_database)
            vws_client = VWS(
                server_access_key=mock_database.server_access_key,
                server_secret_key=mock_database.server_secret_key,
            )

            target_id = vws_client.add_target(
                name='x',
                width=1,
                image=high_quality_image,
                active_flag=True,
                application_metadata=None,
            )

            commands = [
                'wait-for-target-processed',
                '--target-id',
                target_id,
                '--server-access-key',
                mock_database.server_access_key,
                '--server-secret-key',
                mock_database.server_secret_key,
            ]
            result = runner.invoke(vws_group, commands, catch_exceptions=False)
            assert result.exit_code == 0
            assert result.stdout == ''
            report = vws_client.get_database_summary_report()
            expected_requests = (
                # Add target request
                1 +
                # Database summary request
                1 +
                # Initial request
                1 +
                # Request after 0.2 seconds - not processed
                1 +
                # Request after 0.4 seconds - not processed
                # This assumes that there is less than 0.1 seconds taken
                # between the start of the target processing and the start of
                # waiting for the target to be processed.
                1 +
                # Request after 0.6 seconds - processed
                1
            )
            # At the time of writing there is a bug which prevents request
            # usage from being tracked so we cannot track this.
            expected_requests = 0
            assert report['request_usage'] == expected_requests

    def test_custom_seconds_between_requests(
        self,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        It is possible to customize the time waited between polling requests.
        """
        runner = CliRunner()
        with MockVWS(processing_time_seconds=0.5) as mock:
            mock_database = VuforiaDatabase()
            mock.add_database(database=mock_database)
            vws_client = VWS(
                server_access_key=mock_database.server_access_key,
                server_secret_key=mock_database.server_secret_key,
            )

            target_id = vws_client.add_target(
                name='x',
                width=1,
                image=high_quality_image,
                active_flag=True,
                application_metadata=None,
            )

            commands = [
                'wait-for-target-processed',
                '--target-id',
                target_id,
                '--seconds-between-requests',
                '0.3',
                '--server-access-key',
                mock_database.server_access_key,
                '--server-secret-key',
                mock_database.server_secret_key,
            ]
            result = runner.invoke(vws_group, commands, catch_exceptions=False)
            assert result.exit_code == 0
            assert result.stdout == ''
            report = vws_client.get_database_summary_report()
            expected_requests = (
                # Add target request
                1 +
                # Database summary request
                1 +
                # Initial request
                1 +
                # Request after 0.3 seconds - not processed
                # This assumes that there is less than 0.2 seconds taken
                # between the start of the target processing and the start of
                # waiting for the target to be processed.
                1 +
                # Request after 0.6 seconds - processed
                1
            )
            # At the time of writing there is a bug which prevents request
            # usage from being tracked so we cannot track this.
            expected_requests = 0
            assert report['request_usage'] == expected_requests

    def test_custom_seconds_too_small(
        self,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        The minimum valid value for ``--seconds-between-requests`` is 0.05
        seconds.
        """
        runner = CliRunner(mix_stderr=False)
        commands = [
            'wait-for-target-processed',
            '--target-id',
            'x',
            '--seconds-between-requests',
            '0.01',
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code != 0
        assert result.stdout == ''
        expected_substring = (
            '0.01 is smaller than the minimum valid value 0.05'
        )
        assert expected_substring in result.stderr

    def test_custom_timeout(
        self,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        It is possible to set a maximum timeout.
        """
        runner = CliRunner(mix_stderr=False)
        with MockVWS(processing_time_seconds=0.5) as mock:
            mock_database = VuforiaDatabase()
            mock.add_database(database=mock_database)
            vws_client = VWS(
                server_access_key=mock_database.server_access_key,
                server_secret_key=mock_database.server_secret_key,
            )

            target_id = vws_client.add_target(
                name='x',
                width=1,
                image=high_quality_image,
                active_flag=True,
                application_metadata=None,
            )

            report = vws_client.get_target_summary_report(target_id=target_id)
            assert report['status'] == 'processing'

            commands = [
                'wait-for-target-processed',
                '--target-id',
                target_id,
                '--timeout-seconds',
                '0.1',
                '--server-access-key',
                mock_database.server_access_key,
                '--server-secret-key',
                mock_database.server_secret_key,
            ]
            result = runner.invoke(vws_group, commands, catch_exceptions=False)
            assert result.exit_code != 0
            assert result.stderr == 'Timeout of 0.1 seconds reached.\n'

            commands = [
                'wait-for-target-processed',
                '--target-id',
                target_id,
                '--timeout-seconds',
                '0.5',
                '--server-access-key',
                mock_database.server_access_key,
                '--server-secret-key',
                mock_database.server_secret_key,
            ]
            result = runner.invoke(vws_group, commands, catch_exceptions=False)
            assert result.exit_code == 0
            report = vws_client.get_target_summary_report(target_id=target_id)
            assert report['status'] != 'processing'

    def test_custom_timeout_too_small(
        self,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        The minimum valid value for ``--timeout-seconds`` is 0.05 seconds.
        """
        runner = CliRunner(mix_stderr=False)
        commands = [
            'wait-for-target-processed',
            '--target-id',
            'x',
            '--timeout-seconds',
            '0.01',
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code != 0
        expected_substring = (
            '0.01 is smaller than the minimum valid value 0.05'
        )
        assert expected_substring in result.stderr
