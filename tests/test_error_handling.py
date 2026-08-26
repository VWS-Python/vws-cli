"""Tests for shared error handling through public CLI commands."""

import io
from pathlib import Path

import pytest
from click.testing import CliRunner
from mock_vws import MockVWS, VuMarkGenerationFailure
from mock_vws.database import CloudDatabase
from vws import VWS

from vws_cli import vws_group
from vws_cli.vumark import generate_vumark


@pytest.mark.parametrize(
    argnames=("failure", "expected_message"),
    argvalues=[
        pytest.param(
            VuMarkGenerationFailure.AUTHORIZATION_FAILED,
            "Error: The request was not authorized.",
            id="authorization-failed",
        ),
        pytest.param(
            VuMarkGenerationFailure.LICENSE_CHECK_FAILED,
            "Error: The Vuforia license check failed.",
            id="license-check-failed",
        ),
        pytest.param(
            VuMarkGenerationFailure.QUOTA_EXCEEDED,
            "Error: The request quota has been exceeded.",
            id="quota-exceeded",
        ),
    ],
)
def test_vumark_service_error(
    *, failure: VuMarkGenerationFailure, expected_message: str, tmp_path: Path
) -> None:
    """Configured VuMark failures have user-facing messages."""
    database = CloudDatabase()
    with MockVWS(vumark_generation_failure=failure) as mock:
        mock.add_cloud_database(cloud_database=database)
        result = CliRunner().invoke(
            cli=generate_vumark,
            args=[
                "--target-id",
                "targetid",
                "--instance-id",
                "instanceid",
                "--output",
                str(object=tmp_path / "vumark.png"),
                "--server-access-key",
                database.server_access_key,
                "--server-secret-key",
                database.server_secret_key,
            ],
            catch_exceptions=False,
        )

    assert result.exit_code == 1
    assert result.stderr == f"{expected_message}\n"
    assert not result.stdout


def test_invalid_target_type(
    *, high_quality_image: io.BytesIO, tmp_path: Path
) -> None:
    """Generating a VuMark for an image target reports its invalid
    type.
    """
    database = CloudDatabase()
    with MockVWS() as mock:
        mock.add_cloud_database(cloud_database=database)
        target_id = VWS(
            server_access_key=database.server_access_key,
            server_secret_key=database.server_secret_key,
        ).add_target(
            name="image-target",
            width=1,
            image=high_quality_image,
            active_flag=True,
            application_metadata=None,
        )
        result = CliRunner().invoke(
            cli=generate_vumark,
            args=[
                "--target-id",
                target_id,
                "--instance-id",
                "instance-id",
                "--output",
                str(object=tmp_path / "vumark.png"),
                "--server-access-key",
                database.server_access_key,
                "--server-secret-key",
                database.server_secret_key,
            ],
            catch_exceptions=False,
        )

    assert result.exit_code == 1
    assert result.stderr == "Error: The target type is invalid.\n"
    assert not result.stdout


def test_too_many_requests() -> None:
    """A rate-limited public request has a user-facing message."""
    database = CloudDatabase(requests_per_second_limit=0)
    with MockVWS() as mock:
        mock.add_cloud_database(cloud_database=database)
        result = CliRunner().invoke(
            cli=vws_group,
            args=[
                "list-targets",
                "--server-access-key",
                database.server_access_key,
                "--server-secret-key",
                database.server_secret_key,
            ],
            catch_exceptions=False,
        )

    assert result.exit_code == 1
    assert (
        result.stderr
        == "Error: Too many requests were made to Vuforia. Try again later.\n"
    )
    assert not result.stdout
