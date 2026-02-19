"""Tests for VWS CLI VuMark commands."""

import io
import uuid
from pathlib import Path

import pytest
from click.testing import CliRunner
from mock_vws.database import VuforiaDatabase
from vws import VWS

from vws_cli import vws_group


class TestGenerateVuMark:
    """Tests for ``vws generate-vumark``."""

    @staticmethod
    def test_generate_vumark_png(
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """It is possible to generate a VuMark as PNG."""
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        output_file = tmp_path / "output.png"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "12345",
            "--format",
            "png",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        # PNG files start with the PNG magic bytes.
        assert output_file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    @staticmethod
    def test_generate_vumark_svg(
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """It is possible to generate a VuMark as SVG."""
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        output_file = tmp_path / "output.svg"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "12345",
            "--format",
            "svg",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        # SVG files are XML starting with "<".
        assert output_file.read_bytes().startswith(b"<")

    @staticmethod
    def test_generate_vumark_pdf(
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """It is possible to generate a VuMark as PDF."""
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        output_file = tmp_path / "output.pdf"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "12345",
            "--format",
            "pdf",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        # PDF files start with the PDF magic bytes.
        assert output_file.read_bytes().startswith(b"%PDF")

    @staticmethod
    def test_default_format_is_png(
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """The default output format is PNG."""
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        output_file = tmp_path / "output.png"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "12345",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert output_file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    @staticmethod
    def test_unknown_target(
        mock_database: VuforiaDatabase,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the target ID does not exist."""
        runner = CliRunner()
        output_file = tmp_path / "output.png"
        commands = [
            "generate-vumark",
            "--target-id",
            "non-existent-target-id",
            "--instance-id",
            "12345",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 1
        expected_stderr = (
            'Error: Target "non-existent-target-id" does not exist.\n'
        )
        assert result.stderr == expected_stderr

    @staticmethod
    def test_invalid_instance_id(
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the instance ID is invalid."""
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        vws_client.wait_for_target_processed(target_id=target_id)
        output_file = tmp_path / "output.png"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 1
        expected_stderr = "Error: The given instance ID is invalid.\n"
        assert result.stderr == expected_stderr

    @staticmethod
    def test_target_not_in_success_state(
        mock_database: VuforiaDatabase,
        vws_client: VWS,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the target is not in the success
        state.
        """
        runner = CliRunner()
        target_id = vws_client.add_target(
            name=uuid.uuid4().hex,
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        # Do not wait for target to be processed - it will be in processing state.
        output_file = tmp_path / "output.png"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "12345",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_database.server_access_key,
            "--server-secret-key",
            mock_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 1
        expected_stderr = (
            f'Error: The target "{target_id}" is not in the success '
            "state and cannot be used to generate a VuMark instance.\n"
        )
        assert result.stderr == expected_stderr


@pytest.mark.parametrize(argnames="invalid_format", argvalues=["bmp", "gif"])
def test_invalid_format(
    mock_database: VuforiaDatabase,
    tmp_path: Path,
    invalid_format: str,
) -> None:
    """An error is shown for an unrecognised format choice."""
    runner = CliRunner()
    output_file = tmp_path / "output"
    commands = [
        "generate-vumark",
        "--target-id",
        "some-target-id",
        "--instance-id",
        "12345",
        "--format",
        invalid_format,
        "--output",
        str(object=output_file),
        "--server-access-key",
        mock_database.server_access_key,
        "--server-secret-key",
        mock_database.server_secret_key,
    ]
    result = runner.invoke(
        cli=vws_group,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code != 0
