"""teams.py provides AI for computer-controlled teams and functionality regarding all teams.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import Generator, Optional

import pygame

from bombsite.world import playing_field
from bombsite.world.attacks.attack import Attack
from bombsite.world.attacks.rocketlauncher import RocketLauncher
from bombsite.world.characters import characters
from bombsite.world.teams.computer import Computer

colours: list[pygame.Color] = [
    pygame.Color(colour_name)
    for colour_name in ("black", "red", "darkblue", "darkgreen", "yellow", "brown")
]


class Team:
    """A team of allied characters.

    Attributes:
        pf: The playing field in which the team fights.
        team_number: An integer unique to the team amongst all teams on the playing field.
        characters: A list of all characters in the team.
        character_queue: A generator which continually provides the next character to be controlled
            from the team.
        ai: The AI acting on the team, if there is one, otherwise None.
        attack: The present attack the character is using.
    """

    def __init__(self, pf: playing_field.PlayingField, has_ai: bool = False) -> None:
        """Creates the team according to the provided parameters.

        Args:
            pf: The playing field in which the team fights.
            has_ai: Whether or not the team is controlled by an AI.
        """
        self.pf: playing_field.PlayingField = pf
        self.team_number: int = len(pf.teams) + 1
        self.characters: list[characters.Character] = []
        pf.teams.append(self)
        self.character_queue: Generator[characters.Character, None, None] = self.next_character()
        self.ai: Optional[Computer] = self.get_ai(has_ai)
        self.attack: Attack = RocketLauncher()

    def __str__(self) -> str:
        """Returns the team name based on the team number.

        Returns:
            "Team {number}".
        """
        return f"Team {self.team_number}"

    @property
    def colour(self) -> pygame.Color:
        """Returns the colour of the team.

        Returns:
            The RGB colour associated with the team, inferring from the team number.
        """
        return colours[self.team_number - 1]

    def get_ai(self, has_ai: bool) -> Optional[Computer]:
        """Obtains an AI computer player.

        Args:
            has_ai: Whether or not the team is controlled by an AI.

        Returns:
            The AI for the team if computer-controlled, otherwise None.
        """
        return Computer(self) if has_ai else None

    def check_if_alive(self) -> bool:
        """Checks if there are any living characters on the team.

        Returns:
            Returns a boolean for whether there is at least one living character.
        """
        for character in self.characters:
            if character.health.alive:
                return True

        return False

    def next_character(self) -> Generator[characters.Character, None, None]:
        """Continuously cycles over the living characters.

        Yields:
            The next character available to play.
        """
        while True:
            for character in self.characters.copy():
                if character.health.alive:
                    yield character

    def add_character(self, x: int, y: int, name: str) -> characters.Character:
        """Adds a character to the team adhering to certain parameters.

        Args:
            x: The x-position of the character.
            y: The y-position of the character.
            name: The name of the character.

        Returns:
            The newly created character.
        """
        # Creates the character.
        new_character = characters.Character(self.pf, (x, y), name, team=self)

        # Adds the character to the world.
        self.characters.append(new_character)

        return new_character

    def select(self, attack: type[Attack]) -> None:
        """Sets the attack type for the team.

        Args:
            attack: The new attack to be used by the team.
        """
        self.attack = attack()
