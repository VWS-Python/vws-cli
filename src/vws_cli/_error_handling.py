"""Error handling utilities for the VWS CLI."""

from beartype import beartype
from vws.exceptions.custom_exceptions import (
    RecoCountsReportDownloadError,
    RecoCountsReportTimeoutError,
    ServerError,
    TargetProcessingTimeoutError,
)
from vws.exceptions.model_target_exceptions import (
    ModelTargetAuthenticationError,
    ModelTargetDatasetNotDoneError,
    ModelTargetError,
    ModelTargetOAuth2Error,
    ModelTargetValidationError,
    UnknownModelTargetDatasetError,
)
from vws.exceptions.vws_exceptions import (
    AuthenticationFailureError,
    AuthorizationFailedError,
    BadImageError,
    DateRangeError,
    FailError,
    ImageTooLargeError,
    InvalidTargetTypeError,
    LicenseCheckFailedError,
    MetadataTooLargeError,
    ProjectHasNoAPIAccessError,
    ProjectInactiveError,
    ProjectSuspendedError,
    QuotaExceededError,
    RequestQuotaReachedError,
    RequestTimeTooSkewedError,
    TargetNameExistError,
    TargetQuotaReachedError,
    TargetStatusNotSuccessError,
    TargetStatusProcessingError,
    TooManyRequestsError,
    UnknownTargetError,
)


@beartype
def get_error_message(exc: Exception) -> str:
    """Get an error message from a VWS exception."""
    exc_type_to_message: dict[type[Exception], str] = {
        AuthenticationFailureError: "The given secret key was incorrect.",
        AuthorizationFailedError: "Error: The request was not authorized.",
        BadImageError: "Error: The given image is corrupted or the format is not supported.",
        DateRangeError: "Error: There was a problem with the date details given in the request.",
        FailError: "Error: The request made to Vuforia was invalid and could not be processed. Check the given parameters.",
        ImageTooLargeError: "Error: The given image is too large.",
        InvalidTargetTypeError: "Error: The target type is invalid.",
        LicenseCheckFailedError: "Error: The Vuforia license check failed.",
        MetadataTooLargeError: "Error: The given metadata is too large.",
        RecoCountsReportDownloadError: "Error: The recognition counts report could not be downloaded. This may be because the report's URL has expired.",
        RecoCountsReportTimeoutError: "Error: The recognition counts report was not generated within the allowed limit.",
        ServerError: "Error: There was an unknown error from Vuforia. This may be because there is a problem with the given name.",
        ProjectInactiveError: "Error: The project associated with the given keys is inactive.",
        QuotaExceededError: "Error: The request quota has been exceeded.",
        RequestQuotaReachedError: "Error: The maximum number of API calls for this database has been reached.",
        RequestTimeTooSkewedError: "Error: Vuforia reported that the time given with this request was outside the expected range. This may be because the system clock is out of sync.",
        TargetProcessingTimeoutError: "Error: The target processing time has exceeded the allowed limit.",
        TargetQuotaReachedError: "Error: The maximum number of targets for this database has been reached.",
        TooManyRequestsError: "Error: Too many requests were made to Vuforia. Try again later.",
        ProjectSuspendedError: "Error: The request could not be completed because this database has been suspended.",
        ProjectHasNoAPIAccessError: "Error: The request could not be completed because this database is not allowed to make API requests.",
    }

    match exc:
        case UnknownTargetError():
            return f'Error: Target "{exc.target_id}" does not exist.'
        case TargetNameExistError():
            return (
                f'Error: There is already a target named "{exc.target_name}".'
            )
        case TargetStatusNotSuccessError():
            return (
                f'Error: The target "{exc.target_id}" cannot be updated as it is '
                "not in the success state."
            )
        case TargetStatusProcessingError():
            return (
                f'Error: The target "{exc.target_id}" cannot be deleted as it is '
                "in the processing state."
            )
        case _:
            return exc_type_to_message.get(
                type(exc),
                "Error: Vuforia returned an unrecognized error.",
            )


@beartype
def get_model_target_error_message(
    exc: ModelTargetError | ModelTargetOAuth2Error | ServerError,
) -> str:
    """Get an error message from a Model Target Web API exception."""
    match exc:
        case ModelTargetOAuth2Error():
            message = (
                "Error: The given client ID and client secret are not a set "
                "of Model Target Web API credentials."
            )
        # These fallbacks are retained for responses which the public mock
        # cannot produce. Configurable failures and client coverage are
        # tracked upstream in:
        # https://github.com/VWS-Python/vws-python-mock/issues/3495
        # https://github.com/VWS-Python/vws-python/issues/3169
        case ModelTargetAuthenticationError():  # pragma: no cover
            message = "Error: The request to Vuforia was not authenticated."
        case UnknownModelTargetDatasetError():
            message = (
                "Error: No Model Target dataset of the given type matches "
                "the given UUID."
            )
        case ModelTargetDatasetNotDoneError():
            message = (
                "Error: Vuforia has not finished generating the dataset, so "
                "the dataset cannot be downloaded."
            )
        case ModelTargetValidationError():
            problems = [
                f"{detail.code}: {detail.message}" for detail in exc.details
            ] or [exc.message]
            message = "\n".join(
                ["Error: Vuforia rejected the request.", *problems],
            )
        case ModelTargetError():  # pragma: no cover
            message = f"Error: {exc.message or 'Vuforia returned an error.'}"
        case _:  # pragma: no cover
            message = get_error_message(exc=exc)

    return message
