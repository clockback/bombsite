"""mainmenumodule.py is a module active when the user starts Bombsite.

Copyright © 2024 - Elliot Simpson
"""

import pygame

import bombsite.modules.module
import bombsite.ui.mainmenu
from bombsite import settings
from bombsite.modules.modulecomponents import ModuleComponent


class MainMenuModule(bombsite.modules.module.Module):
    """Module for the main menu.

    Attributes:
        screen: The pygame surface onto which everything is drawn.
        mainmenu: The main menu itself.
    """

    def __init__(self, module_component: ModuleComponent) -> None:
        """Initializes the main menu module.

        Args:
            module_component: The semi-custom data to be passed to the module.
        """
        self.screen: pygame.Surface = module_component.screen or pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        self.mainmenu: bombsite.ui.mainmenu.MainMenu = bombsite.ui.mainmenu.MainMenu()

    def process_event(self, event: pygame.event.Event) -> ModuleComponent | None | SystemExit:
        """Handles an incoming main menu event.

        Args:
            event: The most recently polled user event.

        Returns:
            Either None or a game exit.
        """
        # The game quits if given a quit command.
        if event.type == pygame.QUIT:
            return SystemExit()

        # The game quits if the event was the user pressing the escape key.
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return SystemExit()

        else:
            return self.mainmenu.handle(event, self.screen)

    def update(self) -> None:
        """Updates the module over the course of a tick."""

    def render(self) -> None:
        """Displays the main menu onto the screen."""
        self.mainmenu.draw(self.screen)
