"""button.py provides a main menu user interface for beginning games.

Copyright © 2024 - Elliot Simpson
"""

from collections.abc import Callable

import pygame
from pygame.font import Font

from bombsite.modules.modulecomponents import ModuleComponent
from bombsite.settings import UI_PADDING
from bombsite.ui.widgets.widget import Widget
from bombsite.utils import fonts_path


class Button(Widget):
    """A button is a single UI element that triggers an event when clicked."""

    def __init__(
        self, contents: str | pygame.Surface, callback: Callable, *, width: int, font_size: int = 40
    ) -> None:
        """Loads the button.

        Args:
            contents: The text or image displayed in the button.
            callback: The event triggered when the button is clicked.
            width: The width of the button.
            font_size: The font size used for the button text.
        """
        super().__init__()

        self.width: int = width

        normal_render, hover_render = self._get_contents_images(contents, font_size=font_size)

        # Because the hover image is larger, it is used to determine the button size.
        self.height: int = hover_render.get_height() + 2 * UI_PADDING

        # Renders the images for the button itself.
        self.normal_image = self._generate_button_surface(normal_render, self.width, self.height)
        self.hover_image = self._generate_button_surface(hover_render, self.width, self.height)

        self.callback: Callable[[], ModuleComponent | None | SystemExit] = callback

    def _get_contents_images(
        self, contents: str | pygame.Surface, *, font_size: int = 40
    ) -> tuple[pygame.Surface, pygame.Surface]:
        """Finds the images displayed inside the button.

        Args:
            contents: The contents of the button, be they text or an image.
            font_size: The size of any rendered text for the button.

        Returns:
            The two images for the button, relating to when it is being hovered over.
        """
        if isinstance(contents, str):
            # Finds the fonts used in the button.
            normal_font = Font(fonts_path / "playpen_sans" / "PlaypenSans-Regular.ttf", font_size)
            hover_font = Font(fonts_path / "playpen_sans" / "PlaypenSans-Bold.ttf", font_size)

            # Renders the images for the button's contents.
            normal_render = normal_font.render(contents, 1, pygame.color.Color("white"))
            hover_render = hover_font.render(contents, 1, pygame.color.Color("white"))

        # If an image is provided, uses a shrunken image as the normal image.
        else:
            normal_render = pygame.transform.smoothscale(
                contents, (self.width - 10, self.width - 10)
            )
            hover_render = pygame.transform.smoothscale(contents, (self.width - 5, self.width - 5))

        return normal_render, hover_render

    def get_image(self, mouse_x: int, mouse_y: int) -> pygame.Surface:
        """Returns the image of the button.

        Args:
            mouse_x: The x-coordinate of the mouse relative to the button's top-left corner.
            mouse_x: The y-coordinate of the mouse relative to the button's top-left corner.

        Returns:
            The rendering of the button depending on whether or not the cursor is hovering over it.
        """
        if 0 <= mouse_x <= self.width and 0 <= mouse_y <= self.height:
            return self.hover_image
        else:
            return self.normal_image

    def _generate_button_surface(
        self, render: pygame.Surface, width: int, height: int
    ) -> pygame.Surface:
        """Creates an image for the button.

        Args:
            render: The existing image for the text of the button.
            width: The width of the button.
            height: The height of the button.

        Returns:
            A pygame surface conforming to the provided width and height with the button text
            centered therein.
        """
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        render_pos = (
            (surface.get_width() - render.get_width()) / 2,
            (surface.get_height() - render.get_height()) / 2,
        )
        surface.blit(render, render_pos)
        return surface

    def click(self, _mouse_x: int, _mouse_y: int) -> ModuleComponent | None | SystemExit:
        """Responds to a click of the mouse.

        Args:
            _mouse_x: The x-coordinate of the mouse relative to the widget.
            _mouse_y: The y-coordinate of the mouse relative to the widget.
        """
        return self.callback()
