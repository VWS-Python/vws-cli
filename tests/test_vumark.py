"""Tests for VWS CLI VuMark commands."""

import io
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from click.testing import CliRunner
from mock_vws import MockVuMarkWS
from mock_vws.database import VuMarkDatabase
from vws import VuMarkService

from vws_cli import vws_group


@pytest.fixture(name="mock_vumark_database")
def fixture_mock_vumark_database() -> Iterator[VuMarkDatabase]:
    """Yield a mock ``VuMarkDatabase``."""
    with MockVuMarkWS() as mock:
        database = VuMarkDatabase()
        mock.add_database(database=database)
        yield database


@pytest.fixture
def vumark_client(mock_vumark_database: VuMarkDatabase) -> VuMarkService:
    """Return a ``VuMarkService`` client which connects to a mock database."""
    return VuMarkService(
        server_access_key=mock_vumark_database.server_access_key,
        server_secret_key=mock_vumark_database.server_secret_key,
    )


class TestGenerateVuMark:
    """Tests for ``vws generate-vumark``."""

    @staticmethod
    def test_generate_vumark_svg(
        mock_vumark_database: VuMarkDatabase,
        vumark_client: VuMarkService,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """It is possible to generate a VuMark as SVG."""
        runner = CliRunner()
        target_id = vumark_client.add_vumark_target(
            name=uuid.uuid4().hex,
            image=high_quality_image,
        )
        output_file = tmp_path / "output.svg"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "42",
            "--format",
            "svg",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_vumark_database.server_access_key,
            "--server-secret-key",
            mock_vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    @staticmethod
    def test_generate_vumark_png(
        mock_vumark_database: VuMarkDatabase,
        vumark_client: VuMarkService,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """It is possible to generate a VuMark as PNG."""
        runner = CliRunner()
        target_id = vumark_client.add_vumark_target(
            name=uuid.uuid4().hex,
            image=high_quality_image,
        )
        output_file = tmp_path / "output.png"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "42",
            "--format",
            "png",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_vumark_database.server_access_key,
            "--server-secret-key",
            mock_vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    @staticmethod
    def test_generate_vumark_pdf(
        mock_vumark_database: VuMarkDatabase,
        vumark_client: VuMarkService,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """It is possible to generate a VuMark as PDF."""
        runner = CliRunner()
        target_id = vumark_client.add_vumark_target(
            name=uuid.uuid4().hex,
            image=high_quality_image,
        )
        output_file = tmp_path / "output.pdf"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "42",
            "--format",
            "pdf",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_vumark_database.server_access_key,
            "--server-secret-key",
            mock_vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    @staticmethod
    def test_default_format_is_svg(
        mock_vumark_database: VuMarkDatabase,
        vumark_client: VuMarkService,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """The default output format is SVG."""
        runner = CliRunner()
        target_id = vumark_client.add_vumark_target(
            name=uuid.uuid4().hex,
            image=high_quality_image,
        )
        output_file = tmp_path / "output.svg"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "42",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_vumark_database.server_access_key,
            "--server-secret-key",
            mock_vumark_database.server_secret_key,
        ]
        result = runner.invoke(
            cli=vws_group,
            args=commands,
            catch_exceptions=False,
            color=True,
        )
        assert result.exit_code == 0
        assert output_file.exists()
        # SVG files are XML text.
        assert b"<svg" in output_file.read_bytes()

    @staticmethod
    def test_unknown_target(
        mock_vumark_database: VuMarkDatabase,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the target ID does not exist."""
        runner = CliRunner()
        output_file = tmp_path / "output.svg"
        commands = [
            "generate-vumark",
            "--target-id",
            "non-existent-target-id",
            "--instance-id",
            "42",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_vumark_database.server_access_key,
            "--server-secret-key",
            mock_vumark_database.server_secret_key,
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
        mock_vumark_database: VuMarkDatabase,
        vumark_client: VuMarkService,
        high_quality_image: io.BytesIO,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the instance ID is invalid."""
        runner = CliRunner()
        target_id = vumark_client.add_vumark_target(
            name=uuid.uuid4().hex,
            image=high_quality_image,
        )
        output_file = tmp_path / "output.svg"
        commands = [
            "generate-vumark",
            "--target-id",
            target_id,
            "--instance-id",
            "invalid-instance-id!!",
            "--output",
            str(object=output_file),
            "--server-access-key",
            mock_vumark_database.server_access_key,
            "--server-secret-key",
            mock_vumark_database.server_secret_key,
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
