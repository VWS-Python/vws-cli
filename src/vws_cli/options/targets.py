"""``click`` options regarding targets."""

from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import Any

import click
from beartype import beartype

target_id_option: Callable[..., None] = click.option(
    "--target-id",
    type=str,
    help="The ID of a target in the Vuforia database.",
    required=True,
)


@beartype
def target_name_option(*, required: bool) -> Callable[..., None]:
    """An option decorator for choosing a target name."""
    return click.option(
        "--name",
        type=str,
        help="The name of the target in the Vuforia database.",
        required=required,
    )


@beartype
def target_width_option(*, required: bool) -> Callable[..., Any]:
    """An option decorator for choosing a target width."""
    option: Callable[..., Any] = click.option(
        "--width",
        type=float,
        help="The width of the target in the Vuforia database.",
        required=required,
    )
    return option


@beartype
def target_image_option(*, required: bool) -> Callable[..., Any]:
    """An option decorator for choosing a target image."""
    return click.option(
        "--image",
        "image_file_path",
        type=click.Path(
            exists=True,
            file_okay=True,
            dir_okay=False,
            path_type=Path,
        ),
        help="The path to an image to upload and set as the target image.",
        required=required,
    )


class ActiveFlagChoice(Enum):
    """Choices for active flag."""

    TRUE = "true"
    FALSE = "false"


def _active_flag_choice_callback(
    ctx: click.core.Context,
    param: click.core.Option | click.core.Parameter,
    value: str | None,
) -> ActiveFlagChoice | None:
    """Use as a callback for active flag options."""
    # This is to satisfy the "vulture" linter.
    assert ctx
    assert param

    if value is None:
        return None

    return ActiveFlagChoice(value)


def active_flag_option(
    *,
    allow_none: bool,
) -> Callable[..., None]:
    """An option decorator for setting a target's active flag."""
    if allow_none:
        default = None
        show_default = False
    else:
        default = ActiveFlagChoice.TRUE.value
        show_default = True

    return click.option(
        "--active-flag",
        "active_flag_choice",
        help="Whether or not the target is active for query.",
        type=click.Choice(choices=[item.value for item in ActiveFlagChoice]),
        default=default,
        callback=_active_flag_choice_callback,
        show_default=show_default,
    )


application_metadata_option: Callable[..., None] = click.option(
    "--application-metadata",
    type=str,
    required=False,
    help="The base64 encoded application metadata associated with the target.",
)
