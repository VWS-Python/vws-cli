"""Shared typing helpers for Click option decorators."""

from abc import abstractmethod
from collections.abc import Callable
from typing import Protocol, runtime_checkable


@runtime_checkable
class ClickOptionDecorator(Protocol):
    """A decorator which preserves a command's signature."""

    @abstractmethod
    def __call__[**P, R](
        self,
        command: Callable[P, R],
        /,
    ) -> Callable[P, R]:
        """Decorate ``command`` without changing its signature."""
