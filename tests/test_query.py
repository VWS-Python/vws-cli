"""
Test for the Cloud Reco Service commands.
"""

import io
import uuid
from pathlib import Path
from textwrap import dedent

import yaml
from click.testing import CliRunner
from mock_vws import MockVWS
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli.query import vuforia_cloud_reco


class TestQuery:
    """
    Tests for making image queries.
    """

    @staticmethod
    def test_no_matches(
        mock_database: VuforiaDatabase,
        tmp_path: Path,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        An empty list is returned if there are no matches.
        """
        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        result_data = yaml.safe_load(stream=result.stdout)
        assert result_data == []

    @staticmethod
    def test_matches(
        tmp_path: Path,
        high_quality_image: io.BytesIO,
        vws_client: VWS,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        Details of matching targets are shown.
        """
        name = uuid.uuid4().hex
        target_id = vws_client.add_target(
            name=name,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)

        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        result_data = yaml.safe_load(stream=result.stdout)
        [matching_target] = result_data
        target_timestamp = matching_target["target_data"]["target_timestamp"]
        expected_result_data = {
            "target_data": {
                "application_metadata": None,
                "name": name,
                "target_timestamp": target_timestamp,
            },
            "target_id": target_id,
        }
        assert matching_target == expected_result_data

    @staticmethod
    def test_image_file_is_dir(
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        An appropriate error is given if the given image file path points to a
        directory.
        """
        runner = CliRunner()
        commands = [
            str(object=tmp_path),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        expected_result_code = 2
        assert result.exit_code == expected_result_code
        assert not result.stdout
        expected_stderr = dedent(
            text=f"""\
            Usage: vuforia-cloud-reco [OPTIONS] IMAGE
            Try 'vuforia-cloud-reco --help' for help.

            Error: Invalid value for 'IMAGE': File '{tmp_path}' is a directory.
            """,
        ).replace("\\", "\\\\")
        assert result.stderr == expected_stderr

    @staticmethod
    def test_relative_path(
        tmp_path: Path,
        mock_database: VuforiaDatabase,
        high_quality_image: io.BytesIO,
    ) -> None:
        """
        Image file paths are resolved.
        """
        runner = CliRunner()
        new_filename = uuid.uuid4().hex
        original_image_file = tmp_path / "foo"
        image_data = high_quality_image.getvalue()
        original_image_file.write_bytes(data=image_data)
        commands = [
            str(object=new_filename),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        with runner.isolated_filesystem():
            new_file = Path(new_filename)
            new_file.symlink_to(target=original_image_file)
            result = runner.invoke(
                cli=vuforia_cloud_reco,
                args=commands,
                catch_exceptions=False,
                color=True,
            )

        assert result.exit_code == 0
        result_data = yaml.safe_load(stream=result.stdout)
        assert result_data == []

    @staticmethod
    def test_image_file_does_not_exist(
        mock_database: VuforiaDatabase,
        tmp_path: Path,
    ) -> None:
        """
        An appropriate error is given if the given image file does not exist.
        """
        runner = CliRunner()
        does_not_exist_file = tmp_path / uuid.uuid4().hex
        commands = [
            str(object=does_not_exist_file),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        expected_result_code = 2
        assert result.exit_code == expected_result_code
        assert not result.stdout
        expected_stderr = dedent(
            text=f"""\
            Usage: vuforia-cloud-reco [OPTIONS] IMAGE
            Try 'vuforia-cloud-reco --help' for help.

            Error: Invalid value for 'IMAGE': File '{does_not_exist_file}' does not exist.
            """,
        ).replace("\\", "\\\\")
        assert result.stderr == expected_stderr


def test_version() -> None:
    """
    ``vuforia-cloud-reco --version`` shows the version.
    """
    runner = CliRunner()
    commands = ["--version"]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == 0
    assert result.stdout.startswith("vuforia-cloud-reco, version ")


class TestMaxNumResults:
    """
    Tests for the ``--max-num-results`` option.
    """

    @staticmethod
    def test_default(
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        By default the maximum number of results is 1.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        target_id_2 = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        vws_client.wait_for_target_processed(target_id=target_id_2)

        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        result_data = yaml.safe_load(stream=result.stdout)
        assert len(result_data) == 1

    @staticmethod
    def test_custom(
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        It is possible to set a custom ``--max-num-results``.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        target_id_2 = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        target_id_3 = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        vws_client.wait_for_target_processed(target_id=target_id_2)
        vws_client.wait_for_target_processed(target_id=target_id_3)

        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        max_num_results = 2
        commands = [
            str(object=new_file),
            "--max-num-results",
            str(object=max_num_results),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        result_data = yaml.safe_load(stream=result.stdout)
        assert len(result_data) == max_num_results

    @staticmethod
    def test_out_of_range(
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """``--max-num-results`` must be between 1 and 50."""
        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--max-num-results",
            str(object=0),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        expected_result_code = 2
        assert result.exit_code == expected_result_code
        expected_stderr_substring = (
            "Error: Invalid value for '--max-num-results': 0 is not in the "
            "range 1<=x<=50."
        )
        assert expected_stderr_substring in result.stderr


class TestIncludeTargetData:
    """
    Tests for the ``--include-target-data`` option.
    """

    @staticmethod
    def test_default(
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        By default, target data is only returned in the top match.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        target_id_2 = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        vws_client.wait_for_target_processed(target_id=target_id_2)
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--max-num-results",
            str(object=2),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        matches = yaml.safe_load(stream=result.stdout)
        top_match, second_match = matches
        assert top_match["target_data"] is not None
        assert second_match["target_data"] is None

    @staticmethod
    def test_top(
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        When 'top' is given, target data is only returned in the top match.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        target_id_2 = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        vws_client.wait_for_target_processed(target_id=target_id_2)
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--max-num-results",
            str(object=2),
            "--include-target-data",
            "top",
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        matches = yaml.safe_load(stream=result.stdout)
        top_match, second_match = matches
        assert top_match["target_data"] is not None
        assert second_match["target_data"] is None

    @staticmethod
    def test_none(
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        When 'none' is given, target data is not returned in any match.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        target_id_2 = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        vws_client.wait_for_target_processed(target_id=target_id_2)
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--max-num-results",
            str(object=2),
            "--include-target-data",
            "none",
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        matches = yaml.safe_load(stream=result.stdout)
        top_match, second_match = matches
        assert top_match["target_data"] is None
        assert second_match["target_data"] is None

    @staticmethod
    def test_all(
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        When 'all' is given, target data is returned in all matches.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        target_id_2 = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        vws_client.wait_for_target_processed(target_id=target_id_2)
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)

        commands = [
            str(object=new_file),
            "--max-num-results",
            str(object=2),
            "--include-target-data",
            "all",
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        matches = yaml.safe_load(stream=result.stdout)
        top_match, second_match = matches
        assert top_match["target_data"] is not None
        assert second_match["target_data"] is not None

    @staticmethod
    def test_other(
        high_quality_image: io.BytesIO,
        tmp_path: Path,
        mock_database: VuforiaDatabase,
    ) -> None:
        """
        When a string other than 'top', 'all', or 'none' is given, an error is
        shown.
        """
        runner = CliRunner()
        new_file = tmp_path / uuid.uuid4().hex
        image_data = high_quality_image.getvalue()
        new_file.write_bytes(data=image_data)
        commands = [
            str(object=new_file),
            "--max-num-results",
            str(object=2),
            "--include-target-data",
            "other",
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        expected_result_code = 2
        assert result.exit_code == expected_result_code
        expected_stderr = (
            "'--include-target-data': 'other' is not one of 'top', 'none', "
            "'all'."
        )
        assert expected_stderr in result.stderr


def test_base_vwq_url(high_quality_image: io.BytesIO, tmp_path: Path) -> None:
    """
    It is possible to use query a target to a database under a custom VWQ URL.
    """
    runner = CliRunner()
    base_vwq_url = "http://example.com"
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    with MockVWS(base_vwq_url=base_vwq_url) as mock:
        mock_database = VuforiaDatabase()
        mock.add_database(database=mock_database)
        vws_client = VWS(
            server_access_key=mock_database.server_access_key,
            server_secret_key=mock_database.server_secret_key,
        )

        target_id = vws_client.add_target(
            name="x",
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )

        vws_client.wait_for_target_processed(target_id=target_id)

        commands = [
            str(object=new_file),
            "--client-access-key",
            mock_database.client_access_key,
            "--client-secret-key",
            mock_database.client_secret_key,
            "--base-vwq-url",
            base_vwq_url,
        ]
        result = runner.invoke(
            cli=vuforia_cloud_reco,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0

    [match] = yaml.safe_load(stream=result.stdout)
    assert match["target_id"] == target_id


def test_env_var_credentials(
    high_quality_image: io.BytesIO,
    tmp_path: Path,
    mock_database: VuforiaDatabase,
) -> None:
    """
    It is possible to use environment variables to set the credentials.
    """
    runner = CliRunner()
    new_file = tmp_path / uuid.uuid4().hex
    image_data = high_quality_image.getvalue()
    new_file.write_bytes(data=image_data)
    commands = [str(object=new_file)]
    result = runner.invoke(
        cli=vuforia_cloud_reco,
        args=commands,
        catch_exceptions=False,
        color=True,
        env={
            "VUFORIA_CLIENT_ACCESS_KEY": mock_database.client_access_key,
            "VUFORIA_CLIENT_SECRET_KEY": mock_database.client_secret_key,
        },
    )
    assert result.exit_code == 0
