from typing import Callable

import click


def target_id_option(command: Callable[..., None], ) -> Callable[..., None]:
    """
    An option decorator for XXX.
    """
    click_option_function: Callable[[Callable[..., None]], Callable[..., None],
                                    ] = click.option(
                                        '--target-id',
                                        type=str,
                                        help='XXX',
                                        required=True,
                                    )
    function: Callable[..., None] = click_option_function(command)
    return function
