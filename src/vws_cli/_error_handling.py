"""Error handling utilities for the VWS CLI."""

from beartype import beartype
from vws.exceptions.custom_exceptions import (
    ServerError,
    TargetProcessingTimeoutError,
)
from vws.exceptions.vws_exceptions import (
    AuthenticationFailureError,
    BadImageError,
    DateRangeError,
    FailError,
    ImageTooLargeError,
    MetadataTooLargeError,
    ProjectHasNoAPIAccessError,
    ProjectInactiveError,
    ProjectSuspendedError,
    RequestQuotaReachedError,
    RequestTimeTooSkewedError,
    TargetNameExistError,
    TargetQuotaReachedError,
    TargetStatusNotSuccessError,
    TargetStatusProcessingError,
    UnknownTargetError,
)


@beartype
def get_error_message(exc: Exception) -> str:
    """Get an error message from a VWS exception."""
    if isinstance(exc, UnknownTargetError):
        return f'Error: Target "{exc.target_id}" does not exist.'

    if isinstance(exc, TargetNameExistError):
        return f'Error: There is already a target named "{exc.target_name}".'

    if isinstance(exc, TargetStatusNotSuccessError):
        return (
            f'Error: The target "{exc.target_id}" cannot be updated as it is '
            "in the processing state."
        )

    if isinstance(exc, TargetStatusProcessingError):
        return (
            f'Error: The target "{exc.target_id}" cannot be deleted as it is '
            "in the processing state."
        )

    exc_type_to_message: dict[type[Exception], str] = {
        AuthenticationFailureError: "The given secret key was incorrect.",
        BadImageError: "Error: The given image is corrupted or the format is not supported.",
        DateRangeError: "Error: There was a problem with the date details given in the request.",
        FailError: "Error: The request made to Vuforia was invalid and could not be processed. Check the given parameters.",
        ImageTooLargeError: "Error: The given image is too large.",
        MetadataTooLargeError: "Error: The given metadata is too large.",
        ServerError: "Error: There was an unknown error from Vuforia. This may be because there is a problem with the given name.",
        ProjectInactiveError: "Error: The project associated with the given keys is inactive.",
        RequestQuotaReachedError: "Error: The maximum number of API calls for this database has been reached.",
        RequestTimeTooSkewedError: "Error: Vuforia reported that the time given with this request was outside the expected range. This may be because the system clock is out of sync.",
        TargetProcessingTimeoutError: "Error: The target processing time has exceeded the allowed limit.",
        TargetQuotaReachedError: "Error: The maximum number of targets for this database has been reached.",
        ProjectSuspendedError: "Error: The request could not be completed because this database has been suspended.",
        ProjectHasNoAPIAccessError: "Error: The request could not be completed because this database is not allowed to make API requests.",
    }

    return exc_type_to_message[type(exc)]
