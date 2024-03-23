from dataclasses import dataclass
from typing import Optional

import pygame

import bombsite.settings as settings
from bombsite.utils import package_path

pygame.font.init()


@dataclass
class LogMessage:
    text: str
    image: Optional[pygame.Surface]


class Logger:
    """A record of all logged messages to the users."""

    def __init__(self) -> None:
        """Creates the logger."""
        self.messages: list[LogMessage] = []
        self.font: pygame.font.Font = pygame.font.Font(
            package_path / "fonts" / "playpen_sans" / "PlaypenSans-Regular.ttf", 30
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
            self.messages[-settings.LOG_LENGTH].image = None

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
