"""menu.py provides a menu user interface which can host buttons.

Copyright © 2024 - Elliot Simpson
"""

from typing import Callable

import pygame

from bombsite.modules.modulecomponents import ModuleComponent
from bombsite.ui.widgets.button import Button
from bombsite.ui.widgets.widget import Widget


class Menu:
    """The menu containing buttons.

    Attributes:
        widgets: Each widget in the main menu.
    """

    def __init__(self, width: int) -> None:
        """Assigns any attributes to the main menu.

        Args:
            width: The width of the menu.
        """
        self.widgets: list[Widget] = []
        self.width: int = width
        self.height: int = 0

    def add_button(
        self,
        text: str,
        trigger: Callable[[], ModuleComponent | None | SystemExit],
        *,
        width: int,
        font_size: int = 40,
    ) -> None:
        """Adds a button the menu interface.

        Args:
            text: The text in the button.
            trigger: The function called when the button is clicked.
            font_size: The font size used for the button text.
            width: The width of the button.
        """
        button = Button(text, trigger, font_size=font_size, width=width)
        self.widgets.append(button)
        self.width = max([button.get_width(), self.width])
        self.height += button.get_height()

    def get_surface(self, mouse_x: int, mouse_y: int) -> pygame.Surface:
        """Obtains the image of the menu.

        Args:
            mouse_x: The x-coordinate of the mouse relative to the menu's top-left corner.
            mouse_x: The y-coordinate of the mouse relative to the menu's top-left corner.

        Returns:
            The image of the main menu.
        """
        surface = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)

        y = 0
        for widget in self.widgets:
            surface.blit(widget.get_image(mouse_x, mouse_y - y), (0, y))
            y += widget.height

        return surface

    def handle(
        self, event: pygame.event.Event, render_pos: tuple[int, int]
    ) -> ModuleComponent | None | SystemExit:
        """Handles incoming events that interact with the menu widgets.

        Args:
            event: The incoming Pygame event.
            render_pos: The render x- and y- coordinates of the menu.

        Returns:
            Either the new module to be loaded, a SystemExit, or None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x = event.pos[0] - render_pos[0]
            mouse_y = event.pos[1] - render_pos[1]
            return self._click_menu(mouse_x, mouse_y)

        return None

    def _click_menu(self, mouse_x: int, mouse_y: int) -> ModuleComponent | None | SystemExit:
        """Processes a click on the menu.

        Args:
            mouse_x: The x-position of the mouse relative to the menu.
            mouse_y: The y-position of the mouse relative to the menu.
        """
        y = 0
        for widget in self.widgets:
            if 0 <= mouse_x < widget.get_width() and y <= mouse_y < y + widget.get_height():
                return widget.click(mouse_x, mouse_y - y)

            y += widget.height

        return None
