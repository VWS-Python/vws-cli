"""Tests for shared error handling utilities."""

import pytest
from vws.exceptions.base_exceptions import VWSError
from vws.exceptions.vws_exceptions import (
    AuthorizationFailedError,
    InvalidTargetTypeError,
    LicenseCheckFailedError,
    QuotaExceededError,
    TooManyRequestsError,
)
from vws.response import Response

from vws_cli._error_handling import get_error_message


def _response() -> Response:
    """Return a response suitable for constructing a VWS exception."""
    return Response(
        text="error",
        url="https://vws.vuforia.com/targets",
        status_code=400,
        headers={},
        request_body=None,
        tell_position=0,
        content=b"error",
    )


@pytest.mark.parametrize(
    argnames=("exception", "expected_message"),
    argvalues=[
        (
            AuthorizationFailedError(response=_response()),
            "Error: The request was not authorized.",
        ),
        (
            InvalidTargetTypeError(response=_response()),
            "Error: The target type is invalid.",
        ),
        (
            LicenseCheckFailedError(response=_response()),
            "Error: The Vuforia license check failed.",
        ),
        (
            QuotaExceededError(response=_response()),
            "Error: The request quota has been exceeded.",
        ),
        (
            TooManyRequestsError(response=_response()),
            "Error: Too many requests were made to Vuforia. Try again later.",
        ),
        (
            VWSError(response=_response()),
            "Error: Vuforia returned an unrecognized error.",
        ),
    ],
)
def test_vws_error_message(
    *,
    exception: Exception,
    expected_message: str,
) -> None:
    """Every VWS error type has a user-facing message."""
    assert get_error_message(exc=exception) == expected_message
