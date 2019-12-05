"""
``click`` options regarding targets.
"""

from enum import Enum
from typing import Callable

import click
import click_pathlib


def target_id_option(command: Callable[..., None]) -> Callable[..., None]:
    """
    An option decorator for choosing a target ID.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[
        ..., None]] = click.option(
            '--target-id',
            type=str,
            help='The ID of a target in the Vuforia database.',
            required=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function


def target_name_option(command: Callable[..., None]) -> Callable[..., None]:
    """
    An option decorator for choosing a target name.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[
        ..., None]] = click.option(
            '--name',
            type=str,
            help='The name of the target in the Vuforia database.',
            required=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function


def target_width_option(command: Callable[..., None]) -> Callable[..., None]:
    """
    An option decorator for choosing a target width.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[
        ..., None]] = click.option(
            '--width',
            type=float,
            help='The width of the target in the Vuforia database.',
            required=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function


def target_image_option(command: Callable[..., None]) -> Callable[..., None]:
    """
    An option decorator for choosing a target image.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[
        ..., None]] = click.option(
            '--image',
            'image_file_path',
            type=click_pathlib.Path(
                exists=True,
                file_okay=True,
                dir_okay=False,
            ),
            help='The path to an image to upload and set as the target image.',
            required=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function


class ActiveFlagChoice(Enum):
    """
    Choices for active flag.
    """

    TRUE = 'true'
    FALSE = 'false'


def active_flag_option(command: Callable[..., None]) -> Callable[..., None]:
    """
    An option decorator for setting a target's active flag.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[
        ..., None]] = click.option(
            '--active-flag',
            'active_flag_choice',
            type=click.Choice([item.value for item in list(ActiveFlagChoice)]),
            default=ActiveFlagChoice.TRUE.value,
            callback=lambda _, __, value: ActiveFlagChoice(value),
            show_default=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function
