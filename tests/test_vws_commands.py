# pylint:disable=too-many-lines
"""
Tests for VWS CLI commands.
"""

import base64
import io
import random
import uuid
from pathlib import Path
from textwrap import dedent

import pytest
import yaml
from click.testing import CliRunner
from freezegun import freeze_time
from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase
from vws import VWS, CloudRecoService
from vws.reports import TargetStatuses

from vws_cli import vws_group


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
        'target_quota': 1000,
        'total_recos': 0,
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
    result_data = yaml.load(result.stdout, Loader=yaml.FullLoader)
    expected_result_data = [target_id_1, target_id_2]
    # We do not expect a particular order.
    assert sorted(result_data) == sorted(expected_result_data)


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
    upload_date = '2015-04-29'
    with freeze_time(upload_date):
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
        'status': 'success',
        'target_name': 'x',
        'total_recos': 0,
        'tracking_rating': result_data['tracking_rating'],
        'upload_date': upload_date,
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

    def test_add_target(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        cloud_reco_client: CloudRecoService,
    ) -> None:
        """
        It is possible to add a target.
        """
        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        name = uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        width = random.uniform(a=0.01, b=50)
        commands = [
            'add-target',
            '--name',
            name,
            '--width',
            str(width),
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
        target_details = vws_client.get_target_record(target_id=target_id)
        target_record = target_details.target_record
        assert target_record.name == name
        assert target_record.width == width
        assert target_record.active_flag is True
        vws_client.wait_for_target_processed(target_id=target_id)

        [query_result] = cloud_reco_client.query(image=high_quality_image)
        assert query_result.target_id == target_id
        target_data = query_result.target_data
        assert target_data is not None
        assert target_data.application_metadata is None

    def test_image_file_does_not_exist(
        self,
        mock_database: VuforiaDatabase,
        tmp_path: Path,
    ) -> None:
        """
        An appropriate error is given if the given image file does not exist.
        """
        runner = CliRunner(mix_stderr=False)
        does_not_exist_file = tmp_path / uuid.uuid4().hex
        commands = [
            'add-target',
            '--name',
            'foo',
            '--width',
            '1',
            '--image',
            str(does_not_exist_file),
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 2
        assert result.stdout == ''
        expected_stderr = dedent(
            f"""\
            Usage: vws add-target [OPTIONS]
            Try 'vws add-target -h' for help.

            Error: Invalid value for '--image': File '{does_not_exist_file}' does not exist.
            """,  # noqa: E501
        )
        assert result.stderr == expected_stderr

    def test_image_file_is_dir(
        self,
        mock_database: VuforiaDatabase,
        tmp_path: Path,
    ) -> None:
        """
        An appropriate error is given if the given image file path points to a
        directory.
        """
        runner = CliRunner(mix_stderr=False)
        commands = [
            'add-target',
            '--name',
            'foo',
            '--width',
            '1',
            '--image',
            str(tmp_path),
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 2
        assert result.stdout == ''
        expected_stderr = dedent(
            f"""\
            Usage: vws add-target [OPTIONS]
            Try 'vws add-target -h' for help.

            Error: Invalid value for '--image': File '{tmp_path}' is a directory.
            """,  # noqa: E501
        )
        assert result.stderr == expected_stderr

    def test_relative_path(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """
        Image file paths are resolved.
        """
        runner = CliRunner(mix_stderr=False)
        new_filename = uuid.uuid4().hex
        original_image_file = tmp_path / 'foo'
        image_data = high_quality_image.getvalue()
        original_image_file.write_bytes(image_data)
        name = uuid.uuid4().hex
        commands = [
            'add-target',
            '--name',
            name,
            '--width',
            '1',
            '--image',
            new_filename,
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        with runner.isolated_filesystem():
            new_file = Path(new_filename)
            new_file.symlink_to(original_image_file)
            result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 0
        target_id = result.stdout.strip()
        target_record = vws_client.get_target_record(target_id=target_id)
        assert target_record.target_record.name == name

    def test_custom_metadata(
        self,
        mock_database: VuforiaDatabase,
        cloud_reco_client: CloudRecoService,
        vws_client: VWS,
        tmp_path: Path,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        Custom metadata can be given.
        """
        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        name = uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        application_metadata = uuid.uuid4().hex
        metadata_bytes = application_metadata.encode('ascii')
        base64_encoded_metadata_bytes = base64.b64encode(metadata_bytes)
        base64_encoded_metadata = base64_encoded_metadata_bytes.decode('ascii')
        commands = [
            'add-target',
            '--name',
            name,
            '--width',
            '0.1',
            '--image',
            str(new_file),
            '--application-metadata',
            base64_encoded_metadata,
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 0
        target_id = result.stdout.strip()
        vws_client.wait_for_target_processed(target_id=target_id)
        [query_result] = cloud_reco_client.query(image=high_quality_image)
        assert query_result.target_id == target_id
        target_data = query_result.target_data
        assert target_data is not None
        assert target_data.application_metadata == base64_encoded_metadata

    @pytest.mark.parametrize(
        'active_flag_given,active_flag_expected',
        [
            ('true', True),
            ('false', False),
        ],
    )
    def test_custom_active_flag(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        active_flag_given: str,
        active_flag_expected: bool,
    ) -> None:
        """
        The Active Flag of the new target can be chosen.
        """
        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            'add-target',
            '--name',
            'foo',
            '--width',
            '0.1',
            '--image',
            str(new_file),
            '--active-flag',
            active_flag_given,
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 0

        target_id = result.stdout.strip()
        target_details = vws_client.get_target_record(target_id=target_id)
        active_flag = target_details.target_record.active_flag
        assert active_flag is active_flag_expected


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
        assert report.status == TargetStatuses.PROCESSING
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
        assert report.status != TargetStatuses.PROCESSING

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
                1
                +
                # Database summary request
                1
                +
                # Initial request
                1
                +
                # Request after 0.2 seconds - not processed
                1
                +
                # Request after 0.4 seconds - not processed
                # This assumes that there is less than 0.1 seconds taken
                # between the start of the target processing and the start of
                # waiting for the target to be processed.
                1
                +
                # Request after 0.6 seconds - processed
                1
            )
            # At the time of writing there is a bug which prevents request
            # usage from being tracked so we cannot track this.
            expected_requests = 0
            assert report.request_usage == expected_requests

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
                1
                +
                # Database summary request
                1
                +
                # Initial request
                1
                +
                # Request after 0.3 seconds - not processed
                # This assumes that there is less than 0.2 seconds taken
                # between the start of the target processing and the start of
                # waiting for the target to be processed.
                1
                +
                # Request after 0.6 seconds - processed
                1
            )
            # At the time of writing there is a bug which prevents request
            # usage from being tracked so we cannot track this.
            expected_requests = 0
            assert report.request_usage == expected_requests

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
        expected_substring = '0.01 is not in the range x>=0.05.'
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
            assert report.status == TargetStatuses.PROCESSING

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
            assert report.status != TargetStatuses.PROCESSING

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
        expected_substring = '0.01 is not in the range x>=0.05.'
        assert expected_substring in result.stderr


class TestUpdateTarget:
    """
    Tests for ``vws update-target``.
    """

    def test_update_target(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        cloud_reco_client: CloudRecoService,
        different_high_quality_image: io.BytesIO,
    ) -> None:
        """
        It is possible to update a target.
        """
        runner = CliRunner(mix_stderr=False)
        old_name = uuid.uuid4().hex
        old_width = random.uniform(a=0.01, b=50)
        target_id = vws_client.add_target(
            name=old_name,
            width=old_width,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        new_application_metadata = base64.b64encode(b'a').decode('ascii')
        new_name = uuid.uuid4().hex
        new_width = random.uniform(a=0.01, b=50)
        new_image_file = tmp_path / uuid.uuid4().hex
        new_image_data = different_high_quality_image.getvalue()
        new_image_file.write_bytes(data=new_image_data)

        commands = [
            'update-target',
            '--target-id',
            target_id,
            '--name',
            new_name,
            '--width',
            str(new_width),
            '--image',
            str(new_image_file),
            '--active-flag',
            'true',
            '--application-metadata',
            new_application_metadata,
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 0
        assert result.stdout == ''

        vws_client.wait_for_target_processed(target_id=target_id)
        [
            matching_target,
        ] = cloud_reco_client.query(image=different_high_quality_image)
        assert matching_target.target_id == target_id
        query_target_data = matching_target.target_data
        assert query_target_data is not None
        query_metadata = query_target_data.application_metadata
        assert query_metadata == new_application_metadata

        commands = [
            'update-target',
            '--target-id',
            target_id,
            '--active-flag',
            'false',
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 0
        assert result.stdout == ''
        target_details = vws_client.get_target_record(target_id=target_id)
        target_record = target_details.target_record
        assert not target_record.active_flag
        assert target_record.name == new_name
        assert target_record.width == new_width
        assert not target_record.active_flag

    def test_no_fields_given(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        It is possible to give no update fields.
        """
        runner = CliRunner(mix_stderr=False)
        old_name = uuid.uuid4().hex
        old_width = random.uniform(a=0.01, b=50)
        target_id = vws_client.add_target(
            name=old_name,
            width=old_width,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)

        commands = [
            'update-target',
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

    def test_image_file_does_not_exist(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """
        An appropriate error is given if the given image file does not exist.
        """
        target_id = vws_client.add_target(
            name='x',
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        runner = CliRunner(mix_stderr=False)
        does_not_exist_file = tmp_path / uuid.uuid4().hex
        commands = [
            'update-target',
            '--target-id',
            target_id,
            '--image',
            str(does_not_exist_file),
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 2
        assert result.stdout == ''
        expected_stderr = dedent(
            f"""\
            Usage: vws update-target [OPTIONS]
            Try 'vws update-target -h' for help.

            Error: Invalid value for '--image': File '{does_not_exist_file}' does not exist.
            """,  # noqa: E501
        )
        assert result.stderr == expected_stderr

    def test_image_file_is_dir(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """
        An appropriate error is given if the given image file path points to a
        directory.
        """
        target_id = vws_client.add_target(
            name='x',
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        runner = CliRunner(mix_stderr=False)
        commands = [
            'update-target',
            '--target-id',
            target_id,
            '--image',
            str(tmp_path),
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]
        result = runner.invoke(vws_group, commands, catch_exceptions=False)
        assert result.exit_code == 2
        assert result.stdout == ''
        expected_stderr = dedent(
            f"""\
            Usage: vws update-target [OPTIONS]
            Try 'vws update-target -h' for help.

            Error: Invalid value for '--image': File '{tmp_path}' is a directory.
            """,  # noqa: E501
        )
        assert result.stderr == expected_stderr

    def test_relative_path(
        self,
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """
        Image file paths are resolved.
        """
        runner = CliRunner(mix_stderr=False)
        target_id = vws_client.add_target(
            name='x',
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        new_filename = uuid.uuid4().hex
        original_image_file = tmp_path / 'foo'
        image_data = high_quality_image.getvalue()
        original_image_file.write_bytes(image_data)
        commands = [
            'update-target',
            '--target-id',
            target_id,
            '--image',
            new_filename,
            '--server-access-key',
            mock_database.server_access_key,
            '--server-secret-key',
            mock_database.server_secret_key,
        ]

        with runner.isolated_filesystem():
            new_file = Path(new_filename)
            new_file.symlink_to(original_image_file)
            result = runner.invoke(vws_group, commands, catch_exceptions=False)

        assert result.exit_code == 0


def test_custom_base_url() -> None:
    """
    It is possible to use the API to connect to a database under a custom VWS
    URL.
    """
    runner = CliRunner(mix_stderr=False)
    base_vws_url = 'http://example.com'
    mock_database = VuforiaDatabase()
    commands = [
        'list-targets',
        '--server-access-key',
        mock_database.server_access_key,
        '--server-secret-key',
        mock_database.server_secret_key,
        '--base-vws-url',
        base_vws_url,
    ]
    with MockVWS(base_vws_url=base_vws_url) as mock:
        mock.add_database(database=mock_database)
        result = runner.invoke(vws_group, commands, catch_exceptions=False)

    assert result.exit_code == 0
