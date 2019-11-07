from typing import Callable

import click


def server_access_key_option(command: Callable[..., None],
                             ) -> Callable[..., None]:
    """
    An option decorator for XXX.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[..., None],
                                    ] = click.option(
                                        '--server-access-key',
                                        type=str,
                                        help='XXX',
                                        required=True,
                                    )
    function: Callable[..., None] = click_option_function(command)
    return function


def server_secret_key_option(command: Callable[..., None],
                             ) -> Callable[..., None]:
    """
    An option decorator for XXX.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[..., None],
                                    ] = click.option(
                                        '--server-secret-key',
                                        type=str,
                                        help='XXX',
                                        required=True,
                                    )
    function: Callable[..., None] = click_option_function(command)
    return function
