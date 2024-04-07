"""gameplay.py is a module active when the user is actively playing a game.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from bombsite.display import Display
from bombsite.modules.module import Module
from bombsite.modules.modulecomponents import ModuleComponent
from bombsite.modules.moduleenum import ModuleEnum
from bombsite.settings import SCREEN_HEIGHT, SCREEN_WIDTH
from bombsite.ui.attackselector import AttackSelector
from bombsite.world.playing_field import PlayingField
from bombsite.world.teams.teams import Team

if TYPE_CHECKING:
    from bombsite.world.attacks.attack import Attack
    from bombsite.world.world_objects import WorldObject


class GamePlay(Module):
    """Module for an active game.

    Attributes:
        display: The display of the gameplay.
        playing_field: The area in which characters fight.
        focus: The present location to which the display needs to pan, if any, otherwise None.
        attack_selector: The attack selector if it exists, otherwise, otherwise None.
    """

    def __init__(self, module_component: ModuleComponent) -> None:
        """Initializes the gameplay module.

        Args:
            module_component: The semi-custom data to be passed to the module.
        """
        self.display: Display = Display(module_component.get_screen)
        self.playing_field: PlayingField = PlayingField("hills")
        self.focus: tuple[int, int] | None = None
        self.attack_selector: AttackSelector | None = None
        self.test_bombsite()
        self.display.set_focus(*self.playing_field.controlled_character.kinematics.pos.astype(int))

    def test_bombsite(self) -> None:
        """Ensures that the playing field has teams/characters."""
        # Creates the three teams.
        team_1 = Team(self.playing_field)
        team_2 = Team(self.playing_field, has_ai=True)
        team_3 = Team(self.playing_field, has_ai=True)

        # Creates the list of teams.
        self.playing_field.teams.extend([team_1, team_2, team_3])

        # Creates a list of characters.
        characters: list[WorldObject] = [
            team_1.add_character(100, 500, "Joey"),
            team_2.add_character(200, 500, "Ronald"),
            team_3.add_character(300, 500, "Ricky"),
            team_1.add_character(400, 500, "John"),
            team_2.add_character(500, 500, "Tamara"),
            team_3.add_character(600, 500, "Anne"),
            team_1.add_character(700, 500, "Samantha"),
            team_2.add_character(800, 500, "Felicity"),
            team_3.add_character(900, 500, "Alex"),
        ]

        self.playing_field.world_objects = characters
        next(self.playing_field.next_team().character_queue).take_control()

    def process_event(self, event: pygame.event.Event) -> ModuleComponent | None | SystemExit:
        """Handles an incoming gameplay event.

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
            return ModuleComponent(ModuleEnum.MAIN_MENU, screen=self.display.screen)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            character = self.playing_field.controlled_character_or_none
            if character and character.details.team.ai is None:
                character.start_attack()

        # Clicking can be used to interact with the attack selector.
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_LEFT:
            # If it is not the turn of a human-controlled team, ignores the event.
            character = self.playing_field.controlled_character_or_none
            if not character or character.details.team.ai is not None:
                return None

            # Opens the attack selector if not open already.
            if self.attack_selector is None:
                self.attack_selector = AttackSelector(
                    character.details.team, self.close_attack_selector
                )

            # Registers a click on the attack selector otherwise.
            else:
                self.attack_selector.handle(event, self.attack_selector_pos(self.attack_selector))

        return None

    def close_attack_selector(
        self, team: Team | None = None, attack_type: type[Attack] | None = None
    ) -> None:
        """Closes the attack selector and selects the attack for the appropriate team.

        Args:
            team: The team receiving the new attack type.
            attack_type: The new attack type.
        """
        if team is not None and attack_type is not None:
            team.select(attack_type)

        self.attack_selector = None

    def attack_selector_pos(self, attack_selector: AttackSelector) -> tuple[int, int]:
        """Returns the position of the attack selector.

        Args:
            attack_selector: The attack selector interface.

        Returns:
            The x- and y- coordinates of the attack selector.
        """
        return (
            (SCREEN_WIDTH - attack_selector.width) // 2,
            (SCREEN_HEIGHT - attack_selector.height) // 2,
        )

    def update(self) -> None:
        """Updates the module over the course of a tick."""
        # Finds all the keys that are pressed and processes them.
        self.playing_field.process_key_presses(pygame.key.get_pressed())

        self.focus = self.playing_field.update()

    def render(self) -> None:
        """Displays the gameplay onto the screen."""
        self.display.update(self.playing_field, self.focus)

        # Only draws the attack selector interface if it is open.
        if self.attack_selector is not None:
            display_x, display_y = self.attack_selector_pos(self.attack_selector)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.display.screen.blit(
                self.attack_selector.get_surface(mouse_x - display_x, mouse_y - display_y),
                (display_x, display_y),
            )

        pygame.display.flip()
