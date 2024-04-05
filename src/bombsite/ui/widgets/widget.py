"""widget.py provides a UI element abstract base class.

Copyright © 2024 - Elliot Simpson
"""

from abc import ABCMeta, abstractmethod

import pygame

from bombsite.modules.module import ModuleComponent


class Widget(metaclass=ABCMeta):
    """A widget which can be used as a base class for other specific widgets, such as buttons."""

    def __init__(self) -> None:
        """Initializes the widget."""
        self.width: int = 0
        self.height: int = 0

    @abstractmethod
    def get_image(self, mouse_x: int, mouse_y: int) -> pygame.Surface:
        """Retrieves the present image of the widget.

        Args:
            mouse_x: The x-coordinate of the mouse relative to the widget's top-left corner.
            mouse_x: The y-coordinate of the mouse relative to the widget's top-left corner.

        Returns:
            The present rendered surface for the widget.
        """
        return NotImplemented

    def get_width(self) -> int:
        """Returns the widget width.

        Returns:
            The width of the button in pixels.
        """
        return self.width

    def get_height(self) -> int:
        """Returns the widget height.

        Returns:
            The height of the button in pixels.
        """
        return self.height

    def click(self, _mouse_x: int, _mouse_y: int) -> ModuleComponent | None | SystemExit:
        """Responds to a click of the mouse.

        Args:
            _mouse_x: The x-coordinate of the mouse relative to the widget.
            _mouse_y: The y-coordinate of the mouse relative to the widget.
        """
        return None
