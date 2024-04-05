"""logger.py provides functionality to communicate to the players.

Copyright © 2024 - Elliot Simpson
"""

from dataclasses import dataclass
from typing import Optional

import pygame

from bombsite import settings
from bombsite.utils import fonts_path

pygame.font.init()


@dataclass
class LogMessage:
    """A single log message and the corresponding drawn text."""

    text: str
    """The original string to be logged."""

    _image: Optional[pygame.Surface]
    """The rendering of the log message. If the message has expired, the image is discarded."""

    @property
    def image(self) -> pygame.Surface:
        """Obtains the image of the log message.

        Returns:
            The image associated with the log message.

        Raises:
            ValueError: The log message's image has been deleted.
        """
        if self._image is None:
            raise ValueError(f'Log message "{self.text}" no longer has associated image.')

        return self._image

    @image.deleter
    def image(self) -> None:
        """Delete's an image no longer needed for a log message."""
        self._image = None


class Logger:
    """A record of all logged messages to the users.

    Attributes:
        messages: A list of all messages that have entered the log.
        font: The font used for rendering the log messages.
    """

    def __init__(self) -> None:
        """Creates the logger."""
        self.messages: list[LogMessage] = []
        self.font: pygame.font.Font = pygame.font.Font(
            fonts_path / "playpen_sans" / "PlaypenSans-Regular.ttf", 30
        )

    def log(self, text: str) -> None:
        """Adds a new message to the log.

        Args:
            text: The message to be added.
        """
        # Creates a new Log message instance.
        new_message = LogMessage(text, self.font.render(text, False, (0, 0, 0)))

        # Only stores three text images at a time to save memory.
        if len(self.messages) >= settings.LOG_LENGTH:
            del self.messages[-settings.LOG_LENGTH].image

        print(text)

        # Adds the newest message to the log.
        self.messages.append(new_message)

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the log onto the screen.

        Args:
            screen: The surface onto which the log is drawn.
        """
        # Finds the position of the bottom-right corner of the screen.
        x = 5
        y = settings.SCREEN_HEIGHT - 5

        # Iterates over each message and draws it.
        for log in self.messages[: -settings.LOG_LENGTH - 1 : -1]:
            y -= log.image.get_height()
            screen.blit(log.image, (x, y))


logger: Logger = Logger()
