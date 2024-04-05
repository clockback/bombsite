"""mainmenu.py provides a main menu user interface for beginning games.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import pygame

from bombsite.modules.modulecomponents import ModuleComponent
from bombsite.modules.moduleenum import ModuleEnum
from bombsite.settings import UI_PADDING
from bombsite.ui.menu import Menu
from bombsite.utils import images_path, return_system_exit


class MainMenu:
    """The main menu, where users can begin games, or quit.

    Attributes:
        menu: The menu UI used in the main menu.
    """

    def __init__(self) -> None:
        """Assigns any attributes to the main menu."""
        self.image = pygame.image.load(images_path / "logo" / "bombsite.png")
        self.menu = Menu(width=300)

        self.menu.add_button("New Game", self.start_new_game, width=300)
        self.menu.add_button("Quit", return_system_exit, width=300)

    def start_new_game(self) -> ModuleComponent:
        """Begins a new game.

        Returns:
            The new gameplay module to load.
        """
        return ModuleComponent(ModuleEnum.GAMEPLAY, screen=pygame.display.get_surface())

    @property
    def width(self) -> int:
        """Returns the width of the main menu.

        Returns:
            The integer width of the main menu in pixels.
        """
        return max((self.menu.width, self.image.get_width()))

    @property
    def height(self) -> int:
        """Returns the height of the main menu.

        Returns:
            The integer height of the main menu in pixels.
        """
        return self.menu.height + self.image.get_height() + 4 * UI_PADDING

    def main_menu_pos(self, screen: pygame.Surface) -> tuple[int, int]:
        """Returns the position of the main menu relative to the screen.

        Args:
            screen: The screen onto which the menu is drawn.

        Returns:
            A tuple with the x- and y-coordinates of the menu.
        """
        return (
            (screen.get_width() - self.width) // 2,
            (screen.get_height() - self.height) // 2,
        )

    def logo_pos(self, screen: pygame.Surface) -> tuple[int, int]:
        """Returns the position of the main menu relative to the screen.

        Args:
            screen: The screen onto which the menu is drawn.

        Returns:
            A tuple with the x- and y-coordinates of the menu.
        """
        main_menu_x, main_menu_y = self.main_menu_pos(screen)
        return (main_menu_x + (self.width - self.image.get_width()) // 2, main_menu_y)

    def menu_pos(self, screen: pygame.Surface) -> tuple[int, int]:
        """Returns the position of the main menu relative to the screen.

        Args:
            screen: The screen onto which the menu is drawn.

        Returns:
            A tuple with the x- and y-coordinates of the menu.
        """
        main_menu_x, main_menu_y = self.main_menu_pos(screen)
        return (
            main_menu_x + (self.width - self.menu.width) // 2,
            main_menu_y + 4 * UI_PADDING + self.image.get_height(),
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the main menu onto the screen.

        Args:
            screen: The screen onto which the menu is drawn.
        """
        screen.fill(pygame.color.Color("black"))

        screen.blit(self.image, self.logo_pos(screen))

        render_x, render_y = self.menu_pos(screen)
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
        return self.menu.handle(event, self.menu_pos(screen))
