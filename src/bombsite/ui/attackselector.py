"""attackselector.py provides an interface for choosing a weapon.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING

import pygame

from bombsite.modules.modulecomponents import ModuleComponent
from bombsite.ui.widgets.button import Button
from bombsite.world.attacks.rocketlauncher import RocketLauncher
from bombsite.world.attacks.throwgrenade import ThrowGrenade

if TYPE_CHECKING:
    from bombsite.world.attacks.attack import Attack
    from bombsite.world.teams.teams import Team


class AttackSelector:
    """The collection of attacks, where users can decide what to do.

    Attributes:
        team: The team for which the interface is selecting an attack.
        close_function: The function that is called when closing the attack selector interface.
        buttons: The UI used in the attack selection.
        width: The width of the attack selector UI.
        height: The height of the attack selector UI.
    """

    def __init__(self, team: Team, close_function: Callable[[Team, type[Attack]], None]) -> None:
        """Initializes the attack selector with all the different attacks possible.

        Args:
            team: The team using the attack selector.
            close_function: The function that is called when closing the attack selector interface.
        """
        self.team: Team = team
        self.close_function: Callable[[Team, type[Attack]], None] = close_function
        self.buttons: list[Button] = []
        self.width: int = 0
        self.height: int = 0

        self.load_buttons()

    @staticmethod
    def all_attacks() -> list[type[Attack]]:
        """Returns a list of all the attacks that can be used.

        Returns:
            A list of every attack available.
        """
        return [RocketLauncher, ThrowGrenade]

    def load_buttons(self) -> None:
        """Generates each of the buttons in the attack selection."""
        for attack_type in self.all_attacks():
            button = Button(
                attack_type.image(),
                partial(self.close_function, self.team, attack_type),
                width=80,
            )
            self.buttons.append(button)
            self.width += button.get_width()
            self.height = max([button.get_height(), self.height])

    def get_surface(self, mouse_x: int, mouse_y: int) -> pygame.Surface:
        """Obtains the image of the attack selector.

        Args:
            mouse_x: The x-coordinate of the mouse relative to the attack selector's top-left
                corner.
            mouse_x: The y-coordinate of the mouse relative to the attack selector's top-left
                corner.

        Returns:
            The image of the attack selector.
        """
        surface = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        transparent_background = surface.copy()
        transparent_background.fill((255, 255, 255))
        transparent_background.set_alpha(128)
        surface.blit(transparent_background, (0, 0))

        x = 0
        for widget in self.buttons:
            surface.blit(widget.get_image(mouse_x - x, mouse_y), (x, 0))
            x += widget.width

        return surface

    def handle(
        self, event: pygame.event.Event, render_pos: tuple[int, int]
    ) -> ModuleComponent | None | SystemExit:
        """Handles incoming events that interact with the buttons.

        Args:
            event: The incoming Pygame event.
            render_pos: The render x- and y- coordinates of the attack selector.

        Returns:
            Either the new module to be loaded, a SystemExit, or None.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x = event.pos[0] - render_pos[0]
            mouse_y = event.pos[1] - render_pos[1]
            return self._click_attack_selector(mouse_x, mouse_y)

        return None

    def _click_attack_selector(
        self, mouse_x: int, mouse_y: int
    ) -> ModuleComponent | None | SystemExit:
        """Processes a click on the attack selector.

        Args:
            mouse_x: The x-position of the mouse relative to the attack selector.
            mouse_y: The y-position of the mouse relative to the attack selector.
        """
        x = 0
        for button in self.buttons:
            if x <= mouse_x < x + button.get_width() and 0 <= mouse_y < button.get_height():
                return button.click(mouse_x - x, mouse_y)

            x += button.width

        return None
