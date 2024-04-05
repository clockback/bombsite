"""mainmenu.py provides a main menu user interface for beginning games.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import pygame

from bombsite.modules.modulecomponents import ModuleComponent
from bombsite.modules.moduleenum import ModuleEnum
from bombsite.ui.menu import Menu
from bombsite.utils import return_system_exit


class MainMenu:
    """The main menu, where users can begin games, or quit."""

    def __init__(self) -> None:
        """Assigns any attributes to the main menu."""
        self.menu = Menu(width=300)

        self.menu.add_button("New Game", self.start_new_game, width=300)
        self.menu.add_button("Quit", return_system_exit, width=300)

    def start_new_game(self) -> ModuleComponent:
        """Begins a new game.

        Returns:
            The new gameplay module to load.
        """
        return ModuleComponent(ModuleEnum.GAMEPLAY, screen=pygame.display.get_surface())

    def render_pos(self, screen: pygame.Surface) -> tuple[int, int]:
        """Returns the position of the menu component.

        Args:
            screen: The screen onto which the menu is drawn.

        Returns:
            A tuple with the x- and y-coordinates of the menu.
        """
        return (
            (screen.get_width() - self.menu.width) // 2,
            (screen.get_height() - self.menu.height) // 2,
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the main menu onto the screen.

        Args:
            screen: The screen onto which the menu is drawn.
        """
        screen.fill(pygame.color.Color("black"))

        render_x, render_y = self.render_pos(screen)
        mouse_x, mouse_y = pygame.mouse.get_pos()

        menu = self.menu.get_surface(mouse_x - render_x, mouse_y - render_y)
        screen.blit(menu, (render_x, render_y))

        pygame.display.flip()

    def handle(
        self, event: pygame.event.Event, screen: pygame.Surface
    ) -> ModuleComponent | None | SystemExit:
        """Handles incoming events that interact with the menu widgets.

        Args:
            event: The incoming Pygame event.
            screen: The screen onto which the menu is drawn.

        Returns:
            Either the new module to be loaded, a SystemExit, or None.
        """
        return self.menu.handle(event, self.render_pos(screen))
