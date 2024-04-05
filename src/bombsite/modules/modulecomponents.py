"""modulecomponents.py is a data structure passed between modules.

Copyright © 2024 - Elliot Simpson
"""

from dataclasses import dataclass
from typing import TypeVar

from pygame import Surface

from bombsite.modules.moduleenum import ModuleEnum

T = TypeVar("T")


@dataclass
class ModuleComponent:
    """A data structure that is used by modules to construct other modules."""

    module_reference: ModuleEnum
    screen: Surface | None = None

    @staticmethod
    def get_non_null_or_fail(value: T | None) -> T:
        """Returns the provided value, but does not allow None values.

        Args:
            value: The value, to be tested against being None.

        Returns:
            The non-None value.
        """
        if value is None:
            raise AttributeError("Expected value but got None.")

        return value

    @property
    def get_screen(self) -> Surface:
        """Gets the value of screen, but fails if the value is None.

        Returns:
            The non-None value of screen.
        """
        return self.get_non_null_or_fail(self.screen)
