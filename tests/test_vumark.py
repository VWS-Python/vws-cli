"""Tests for the ``vumark`` CLI command."""

import io
import uuid
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from mock_vws.database import CloudDatabase, VuMarkDatabase
from mock_vws.target import VuMarkTarget
from vws import VWS

from vws_cli import vumark as vumark_module

generate_vumark = vumark_module.generate_vumark


class TestGenerateVuMark:
    """Tests for ``vumark``."""

    @staticmethod
    @pytest.mark.parametrize(
        argnames=("format_name", "expected_prefix"),
        argvalues=[
            pytest.param("png", b"\x89PNG\r\n\x1a\n", id="png"),
            pytest.param("svg", b"<", id="svg"),
            pytest.param("pdf", b"%PDF", id="pdf"),
        ],
    )
    def test_generate_vumark_format(
        vumark_database: VuMarkDatabase,
        vumark_target: VuMarkTarget,
        tmp_path: Path,
        format_name: str,
        expected_prefix: bytes,
    ) -> None:
        """The returned file matches the requested format."""
        runner = CliRunner()
        output_file = tmp_path / f"output.{format_name}"
        commands = [
            "--target-id",
            vumark_target.target_id,
            "--instance-id",
            "12345",
            "--format",
            format_name,
            "--output",
            str(object=output_file),
            "--server-access-key",
            vumark_database.server_access_key,
            "--server-secret-key",
            vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=generate_vumark,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.read_bytes().startswith(expected_prefix)

    @staticmethod
    def test_default_format_is_png(
        vumark_database: VuMarkDatabase,
        vumark_target: VuMarkTarget,
        tmp_path: Path,
    ) -> None:
        """The default output format is png."""
        runner = CliRunner()
        output_file = tmp_path / "output.png"
        commands = [
            "--target-id",
            vumark_target.target_id,
            "--instance-id",
            "12345",
            "--output",
            str(object=output_file),
            "--server-access-key",
            vumark_database.server_access_key,
            "--server-secret-key",
            vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=generate_vumark,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert output_file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    @staticmethod
    def test_unknown_target(
        vumark_database: VuMarkDatabase,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the target ID does not exist."""
        nonexistent_target_id = uuid.uuid4().hex
        runner = CliRunner()
        output_file = tmp_path / "output.png"
        commands = [
            "--target-id",
            nonexistent_target_id,
            "--instance-id",
            "12345",
            "--output",
            str(object=output_file),
            "--server-access-key",
            vumark_database.server_access_key,
            "--server-secret-key",
            vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=generate_vumark,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 1
        expected_stderr = (
            f'Error: Target "{nonexistent_target_id}" does not exist.\n'
        )
        assert result.stderr == expected_stderr

    @staticmethod
    def test_invalid_instance_id(
        vumark_database: VuMarkDatabase,
        vumark_target: VuMarkTarget,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the instance ID is invalid."""
        runner = CliRunner()
        output_file = tmp_path / "output.png"
        commands = [
            "--target-id",
            vumark_target.target_id,
            "--instance-id",
            "",
            "--output",
            str(object=output_file),
            "--server-access-key",
            vumark_database.server_access_key,
            "--server-secret-key",
            vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=generate_vumark,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 1
        expected_stderr = "Error: The given instance ID is invalid.\n"
        assert result.stderr == expected_stderr

    @staticmethod
    @pytest.mark.xfail(
        reason="mock-vws does not yet validate target status for VuMark",
        strict=True,
    )
    def test_target_not_in_success_state(
        mock_database: CloudDatabase,
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
            cli=generate_vumark,
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
    mock_database: CloudDatabase,
    tmp_path: Path,
    invalid_format: str,
) -> None:
    """An error is shown for an unrecognized format choice."""
    runner = CliRunner()
    output_file = tmp_path / "output"
    commands = [
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
        cli=generate_vumark,
        args=commands,
        catch_exceptions=False,
        color=True,
    )
    assert result.exit_code == click.UsageError.exit_code
    expected_output = (
        "Usage: vumark [OPTIONS]\n"
        "Try 'vumark --help' for help.\n"
        "\n"
        f"Error: Invalid value for '--format': '{invalid_format}' is not "
        "one of 'png', 'svg', 'pdf'.\n"
    )
    assert result.output == expected_output
