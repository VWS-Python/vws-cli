"""``click`` options regarding targets."""

from __future__ import annotations

import functools
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from collections.abc import Callable


def target_id_option(command: Callable[..., None]) -> Callable[..., None]:
    """An option decorator for choosing a target ID."""
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        "--target-id",
        type=str,
        help="The ID of a target in the Vuforia database.",
        required=True,
    )
    function: Callable[..., None] = click_option_function(command)
    return function


def target_name_option(
    command: Callable[..., None] | None,
    *,
    required: bool,
) -> Callable[..., None]:
    """An option decorator for choosing a target name."""
    if not command:
        # Ignore type error as per https://github.com/python/mypy/issues/1484.
        return functools.partial(  # type: ignore[return-value]
            target_name_option,
            required=required,
        )
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        "--name",
        type=str,
        help="The name of the target in the Vuforia database.",
        required=required,
    )
    function: Callable[..., None] = click_option_function(command)
    return function


def optional_target_width_option(
    command: Callable[..., None] | None,
) -> Callable[..., None]:
    """An option decorator for choosing a target width."""
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        "--width",
        type=float,
        help="The width of the target in the Vuforia database.",
        required=False,
    )
    assert command is not None
    function: Callable[..., None] = click_option_function(command)
    return function


def required_target_width_option(
    command: Callable[..., None] | None,
) -> Callable[..., None]:
    """An option decorator for choosing a target width."""
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        "--width",
        type=float,
        help="The width of the target in the Vuforia database.",
        required=True,
    )
    assert command is not None
    function: Callable[..., None] = click_option_function(command)
    return function


def target_image_option(
    command: Callable[..., None] | None,
    *,
    required: bool,
) -> Callable[..., None]:
    """An option decorator for choosing a target image."""
    if not command:
        # Ignore type error as per https://github.com/python/mypy/issues/1484.
        return functools.partial(  # type: ignore[return-value]
            target_image_option,
            required=required,
        )

    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
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

    function: Callable[..., None] = click_option_function(command)
    return function


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
    command: Callable[..., None] | None,
    *,
    allow_none: bool,
) -> Callable[..., None]:
    """An option decorator for setting a target's active flag."""
    if not command:
        # Ignore type error as per https://github.com/python/mypy/issues/1484.
        return functools.partial(  # type: ignore[return-value]
            active_flag_option,
            allow_none=allow_none,
        )

    if allow_none:
        default = None
        show_default = False
    else:
        default = ActiveFlagChoice.TRUE.value
        show_default = True

    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        "--active-flag",
        "active_flag_choice",
        help="Whether or not the target is active for query.",
        type=click.Choice([item.value for item in ActiveFlagChoice]),
        default=default,
        callback=_active_flag_choice_callback,
        show_default=show_default,
    )
    function: Callable[..., None] = click_option_function(command)
    return function


def application_metadata_option(
    command: Callable[..., None] | None = None,
) -> Callable[..., None]:
    """An option decorator for setting application metadata."""
    click_option_function: Callable[
        [Callable[..., None]],
        Callable[..., None],
    ] = click.option(
        "--application-metadata",
        type=str,
        required=False,
        help=(
            "The base64 encoded application metadata associated with the "
            "target."
        ),
    )
    assert command is not None
    function: Callable[..., None] = click_option_function(command)
    return function
