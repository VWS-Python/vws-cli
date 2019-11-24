"""
``click`` options regarding targets.
"""

from typing import Callable

import click


def target_id_option(command: Callable[..., None]) -> Callable[..., None]:
    """
    An option decorator for choosing a target ID.
    """
    click_option_function: Callable[
        [Callable[..., None]], Callable[..., None]] = click.option(
            '--target-id',
            type=str,
            help='The ID of a target in the Vuforia database.',
            required=True,
        )
    function: Callable[..., None] = click_option_function(command)
    return function
