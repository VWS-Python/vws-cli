"""
Tools for handling errors from VWS and the Cloud Reco Service.
"""

import sys
from typing import Any, Callable, Dict, Tuple

import click
import wrapt
from requests import codes
from vws.exceptions import (
    AuthenticationFailure,
    BadImage,
    ConnectionErrorPossiblyImageTooLarge,
    DateRangeError,
    Fail,
    ImageTooLarge,
    MatchProcessing,
    MetadataTooLarge,
    ProjectHasNoAPIAccess,
    ProjectInactive,
    ProjectSuspended,
    RequestQuotaReached,
    RequestTimeTooSkewed,
    TargetNameExist,
    TargetQuotaReached,
    TargetStatusNotSuccess,
    TargetStatusProcessing,
    UnknownTarget,
    UnknownVWSErrorPossiblyBadName,
)


@wrapt.decorator
def handle_vws_exceptions(
    wrapped: Callable[..., str],
    instance: Any,
    args: Tuple,
    kwargs: Dict,
) -> None:
    """
    Show error messages and catch exceptions for errors from the ``VWS-Python``
    library.
    """
    assert not instance  # This is to satisfy the "vulture" linter.
    try:
        wrapped(*args, **kwargs)
    except UnknownTarget as exc:
        error_message = f'Error: Target "{exc.target_id}" does not exist.'
    except BadImage:
        error_message = (
            'Error: The given image is corrupted or the format is not '
            'supported.'
        )
    except Fail as exc:
        assert exc.response.status_code == codes.BAD_REQUEST
        error_message = (
            'Error: The request made to Vuforia was invalid and could not be '
            'processed. '
            'Check the given parameters.'
        )
    except MetadataTooLarge:
        error_message = 'Error: The given metadata is too large.'
    except ImageTooLarge:
        error_message = 'Error: The given image is too large.'
    except TargetNameExist as exc:
        error_message = (
            f'Error: There is already a target named "{exc.target_name}".'
        )
    except ProjectInactive:
        error_message = (
            'Error: The project associated with the given keys is inactive.'
        )
    except UnknownVWSErrorPossiblyBadName:
        error_message = (
            'Error: There was an unknown error from Vuforia. '
            'This may be because there is a problem with the given name.'
        )
    except TargetStatusProcessing as exc:
        error_message = (
            f'Error: The target "{exc.target_id}" cannot be deleted as it is '
            'in the processing state.'
        )
    except TargetStatusNotSuccess as exc:
        error_message = (
            f'Error: The target "{exc.target_id}" cannot be updated as it is '
            'in the processing state.'
        )
    except AuthenticationFailure:
        error_message = 'The given secret key was incorrect.'
    except RequestTimeTooSkewed:
        error_message = (
            'Error: Vuforia reported that the time given with this request '
            'was outside the expected range. '
            'This may be because the system clock is out of sync.'
        )
    # This exception is not available from the mock.
    except RequestQuotaReached:  # pragma: no cover
        error_message = (
            'Error: The maximum number of API calls for this database has '
            'been reached.'
        )
    # This exception is not available from the mock.
    except DateRangeError:  # pragma: no cover
        error_message = (
            'Error: There was a problem with the date details given in the '
            'request.'
        )
    # This exception is not available from the mock.
    except TargetQuotaReached:  # pragma: no cover
        error_message = (
            'Error: The maximum number of targets for this database has been '
            'reached.'
        )
    # This exception is not available from the mock.
    except ProjectSuspended:  # pragma: no cover
        error_message = (
            'Error: The request could not be completed because this database '
            'has been suspended.'
        )
    # This exception is not available from the mock.
    except ProjectHasNoAPIAccess:  # pragma: no cover
        error_message = (
            'Error: The request could not be completed because this database '
            'is not allowed to make API requests.'
        )
    except ConnectionErrorPossiblyImageTooLarge:
        error_message = 'Error: The given image is too large.'
    except MatchProcessing:
        error_message = (
            'Error: The given image matches a target which was recently '
            'added, updated or deleted and Vuforia returns an error in this '
            'case.'
        )
    else:
        return

    click.echo(error_message, err=True)
    sys.exit(1)
