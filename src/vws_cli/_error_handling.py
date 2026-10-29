"""Error handling utilities for the VWS CLI."""

from beartype import beartype
from vws.exceptions.custom_exceptions import (
    ServerError,
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
    FailError,
    InvalidTargetTypeError,
    LicenseCheckFailedError,
    ProjectHasNoAPIAccessError,
    ProjectInactiveError,
    ProjectSuspendedError,
    QuotaExceededError,
    RequestQuotaReachedError,
    RequestTimeTooSkewedError,
    TooManyRequestsError,
)


@beartype
def get_error_message(exc: Exception) -> str:
    """Get an error message from a VWS exception."""
    exc_type_to_message: dict[type[Exception], str] = {
        AuthenticationFailureError: "The given secret key was incorrect.",
        AuthorizationFailedError: "Error: The request was not authorized.",
        FailError: "Error: The request made to Vuforia was invalid and could not be processed. Check the given parameters.",
        InvalidTargetTypeError: "Error: The target type is invalid.",
        LicenseCheckFailedError: "Error: The Vuforia license check failed.",
        ServerError: "Error: There was an unknown error from Vuforia. This may be because there is a problem with the given name.",
        ProjectInactiveError: "Error: The project associated with the given keys is inactive.",
        QuotaExceededError: "Error: The request quota has been exceeded.",
        RequestQuotaReachedError: "Error: The maximum number of API calls for this database has been reached.",
        RequestTimeTooSkewedError: "Error: Vuforia reported that the time given with this request was outside the expected range. This may be because the system clock is out of sync.",
        TooManyRequestsError: "Error: Too many requests were made to Vuforia. Try again later.",
        ProjectSuspendedError: "Error: The request could not be completed because this database has been suspended.",
        ProjectHasNoAPIAccessError: "Error: The request could not be completed because this database is not allowed to make API requests.",
    }

    return exc_type_to_message.get(
        type(exc),
        "Error: Vuforia returned an unrecognized error.",
    )


@beartype
def get_model_target_error_message(
    exc: (
        ModelTargetError
        | ModelTargetOAuth2Error
        | ServerError
        | TooManyRequestsError
    ),
) -> str:
    """Get an error message from a Model Target Web API exception."""
    match exc:
        case ModelTargetOAuth2Error():
            message = (
                "Error: The given client ID and client secret are not a set "
                "of Model Target Web API credentials."
            )
        case ModelTargetAuthenticationError():
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
            ]
            if len(problems) == 0:
                problems = [exc.message]
            message = "\n".join(
                ["Error: Vuforia rejected the request.", *problems],
            )
        case ModelTargetError():
            error_message = (
                exc.message
                if exc.message != ""
                else "Vuforia returned an error."
            )
            message = f"Error: {error_message}"
        case _:
            message = get_error_message(exc=exc)

    return message
