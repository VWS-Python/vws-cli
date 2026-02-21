"""Tests for the ``vumark`` CLI command."""

import io
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from click.testing import CliRunner
from mock_vws.database import CloudDatabase
from vws import VWS
from vws.exceptions.base_exceptions import VWSError
from vws.exceptions.custom_exceptions import ServerError
from vws.exceptions.vws_exceptions import (
    AuthenticationFailureError,
    FailError,
    InvalidInstanceIdError,
    InvalidTargetTypeError,
    ProjectHasNoAPIAccessError,
    ProjectInactiveError,
    ProjectSuspendedError,
    RequestQuotaReachedError,
    RequestTimeTooSkewedError,
    TargetStatusNotSuccessError,
    UnknownTargetError,
)
from vws.response import Response
from vws.vumark_accept import VuMarkAccept

from vws_cli import vumark as vumark_module

if TYPE_CHECKING:
    from collections.abc import Callable

generate_vumark = vumark_module.generate_vumark
_GET_VUMARK_ERROR_MESSAGE_NAME = "_get_vumark_error_message"
get_vumark_error_message = cast(
    "Callable[[Exception], str]",
    getattr(vumark_module, _GET_VUMARK_ERROR_MESSAGE_NAME),
)


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
    def test_generate_vumark_format(  # pylint: disable=too-many-positional-arguments
        monkeypatch: pytest.MonkeyPatch,
        mock_database: CloudDatabase,
        tmp_path: Path,
        format_name: str,
        expected_prefix: bytes,
    ) -> None:
        """The returned file matches the requested format."""
        format_to_output_bytes = {
            VuMarkAccept.PNG: b"\x89PNG\r\n\x1a\nfake-png",
            VuMarkAccept.SVG: b"<svg></svg>",
            VuMarkAccept.PDF: b"%PDF-1.7\n",
        }

        def mock_generate_vumark_instance(
            _self: object,
            *,
            target_id: str,
            instance_id: str,
            accept: VuMarkAccept,
        ) -> bytes:
            """Return fake bytes for the requested format."""
            assert target_id == "some-target-id"
            assert instance_id == "12345"
            return format_to_output_bytes[accept]

        monkeypatch.setattr(
            target=vumark_module.VuMarkService,
            name="generate_vumark_instance",
            value=mock_generate_vumark_instance,
        )

        runner = CliRunner()
        output_file = tmp_path / f"output.{format_name}"
        commands = [
            "--target-id",
            "some-target-id",
            "--instance-id",
            "12345",
            "--format",
            format_name,
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
        assert result.exit_code == 0
        assert output_file.read_bytes().startswith(expected_prefix)

    @staticmethod
    def test_default_format_is_png(
        monkeypatch: pytest.MonkeyPatch,
        mock_database: CloudDatabase,
        tmp_path: Path,
    ) -> None:
        """The default output format is png."""

        def mock_generate_vumark_instance(
            _self: object,
            *,
            target_id: str,
            instance_id: str,
            accept: VuMarkAccept,
        ) -> bytes:
            """Return fake PNG bytes."""
            assert target_id == "some-target-id"
            assert instance_id == "12345"
            assert accept is VuMarkAccept.PNG
            return b"\x89PNG\r\n\x1a\nfake-png"

        monkeypatch.setattr(
            target=vumark_module.VuMarkService,
            name="generate_vumark_instance",
            value=mock_generate_vumark_instance,
        )

        runner = CliRunner()
        output_file = tmp_path / "output.png"
        commands = [
            "--target-id",
            "some-target-id",
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
        assert result.exit_code == 0
        assert output_file.exists()
        assert output_file.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

    @staticmethod
    @pytest.mark.xfail(
        reason="mock-vws does not yet handle unknown targets for VuMark",
        strict=True,
    )
    def test_unknown_target(
        mock_database: CloudDatabase,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the target ID does not exist."""
        runner = CliRunner()
        output_file = tmp_path / "output.png"
        commands = [
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
            cli=generate_vumark,
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
        monkeypatch: pytest.MonkeyPatch,
        mock_database: CloudDatabase,
        tmp_path: Path,
    ) -> None:
        """An error is shown when the instance ID is invalid."""

        def mock_generate_vumark_instance(
            _self: object,
            *,
            target_id: str,
            instance_id: str,
            accept: VuMarkAccept,
        ) -> bytes:
            """Raise InvalidInstanceIdError for an empty instance ID."""
            assert target_id == "some-target-id"
            assert instance_id == ""
            assert accept is VuMarkAccept.PNG
            raise InvalidInstanceIdError(
                response=_response_for_target(target_id=target_id),
            )

        monkeypatch.setattr(
            target=vumark_module.VuMarkService,
            name="generate_vumark_instance",
            value=mock_generate_vumark_instance,
        )

        runner = CliRunner()
        output_file = tmp_path / "output.png"
        commands = [
            "--target-id",
            "some-target-id",
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
    assert result.exit_code != 0


def _response_for_target(target_id: str = "some-target-id") -> Response:
    """Build a minimal VWS response for exception construction in
    tests.
    """
    return Response(
        text="{}",
        url=f"https://vws.vuforia.com/targets/{target_id}",
        status_code=400,
        headers={},
        request_body=None,
        tell_position=0,
        content=b"",
    )


@pytest.mark.parametrize(
    argnames=("exception_type", "expected_message"),
    argvalues=[
        pytest.param(
            InvalidInstanceIdError,
            "Error: The given instance ID is invalid.",
            id="invalid_instance_id",
        ),
        pytest.param(
            InvalidTargetTypeError,
            "Error: The target is not a VuMark template target.",
            id="invalid_target_type",
        ),
        pytest.param(
            AuthenticationFailureError,
            "The given secret key was incorrect.",
            id="authentication_failure",
        ),
        pytest.param(
            FailError,
            (
                "Error: The request made to Vuforia was invalid and could "
                "not be processed. Check the given parameters."
            ),
            id="fail_error",
        ),
        pytest.param(
            RequestTimeTooSkewedError,
            (
                "Error: Vuforia reported that the time given with this "
                "request was outside the expected range. This may be "
                "because the system clock is out of sync."
            ),
            id="request_time_too_skewed",
        ),
        pytest.param(
            ServerError,
            "Error: There was an unknown error from Vuforia.",
            id="server_error",
        ),
        pytest.param(
            ProjectInactiveError,
            "Error: The project associated with the given keys is inactive.",
            id="project_inactive",
        ),
        pytest.param(
            RequestQuotaReachedError,
            (
                "Error: The maximum number of API calls for this database "
                "has been reached."
            ),
            id="request_quota_reached",
        ),
        pytest.param(
            ProjectSuspendedError,
            (
                "Error: The request could not be completed because this "
                "database has been suspended."
            ),
            id="project_suspended",
        ),
        pytest.param(
            ProjectHasNoAPIAccessError,
            (
                "Error: The request could not be completed because this "
                "database is not allowed to make API requests."
            ),
            id="project_has_no_api_access",
        ),
    ],
)
def test_get_vumark_error_message(
    exception_type: type[VWSError] | type[ServerError],
    expected_message: str,
) -> None:
    """Expected message is returned for mapped exceptions."""
    exc = exception_type(response=_response_for_target())
    assert get_vumark_error_message(exc) == expected_message


def test_get_vumark_error_message_for_unknown_target() -> None:
    """Unknown target message includes the target ID."""
    target_id = "target-id-from-url"
    exc = UnknownTargetError(
        response=_response_for_target(target_id=target_id)
    )
    assert (
        get_vumark_error_message(exc)
        == f'Error: Target "{target_id}" does not exist.'
    )


def test_get_vumark_error_message_for_target_not_success() -> None:
    """Target status message includes the target ID."""
    target_id = "target-id-from-url"
    exc = TargetStatusNotSuccessError(
        response=_response_for_target(target_id=target_id),
    )
    assert get_vumark_error_message(exc) == (
        f'Error: The target "{target_id}" is not in the success state and '
        "cannot be used to generate a VuMark instance."
    )


def test_get_vumark_error_message_for_unexpected_vws_error() -> None:
    """Unexpected VWS errors fall back to a generic message."""

    class UnexpectedVWSError(VWSError):
        """A VWS error type not explicitly mapped in vws-cli."""

    exc = UnexpectedVWSError(response=_response_for_target())
    assert (
        get_vumark_error_message(exc)
        == "Error: There was an unexpected error from Vuforia."
    )
