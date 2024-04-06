"""gameplay.py is a module active when the user is actively playing a game.

Copyright © 2024 - Elliot Simpson
"""

from typing import TYPE_CHECKING

import pygame

from bombsite.display import Display
from bombsite.modules.module import Module
from bombsite.modules.modulecomponents import ModuleComponent
from bombsite.modules.moduleenum import ModuleEnum
from bombsite.world.playing_field import PlayingField
from bombsite.world.teams.teams import Team

if TYPE_CHECKING:
    from bombsite.world.world_objects import WorldObject


class GamePlay(Module):
    """Module for an active game.

    Attributes:
        display: The display of the gameplay.
        playing_field: The area in which characters fight.
        focus: The present location to which the display needs to pan, if any, otherwise None.
    """

    def __init__(self, module_component: ModuleComponent) -> None:
        """Initializes the gameplay module.

        Args:
            module_component: The semi-custom data to be passed to the module.
        """
        self.display: Display = Display(module_component.get_screen)
        self.playing_field: PlayingField = PlayingField("hills")
        self.focus: tuple[int, int] | None = None
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

        return None

    def update(self) -> None:
        """Updates the module over the course of a tick."""
        # Finds all the keys that are pressed and processes them.
        self.playing_field.process_key_presses(pygame.key.get_pressed())

        self.focus = self.playing_field.update()

    def render(self) -> None:
        """Displays the gameplay onto the screen."""
        self.display.update(self.playing_field, self.focus)
