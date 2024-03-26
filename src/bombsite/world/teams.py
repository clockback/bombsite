"""teams.py provides AI for computer-controlled teams and functionality regarding all teams.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import Generator, Optional

import numpy as np
import numpy.typing as npt
import pygame

from bombsite import settings
from bombsite.world import playing_field, world_objects
from bombsite.world.characters import characters
from bombsite.world.projectiles.rocket import Rocket

colours: list[pygame.Color] = [
    pygame.Color(colour_name)
    for colour_name in ("black", "red", "darkblue", "darkgreen", "yellow", "brown")
]


class Computer:
    """A computer AI which can issue commands to the characters.

    Attributes:
        team: The team the AI applies to.
        targeting_character: The character that the AI has most recently decided to attack.
        time_to_act:
    """

    def __init__(self, team: Team) -> None:
        """Creates the computer according to the provided parameters.

        Args:
            team: The team which has the computer AI.
        """
        self.team: Team = team
        self.targeting_character: Optional[world_objects.Character] = None
        self.time_to_act: bool = True
        self.destination: Optional[npt.NDArray[np.int_]]
        self.is_firing_left: Optional[bool] = None
        self.firing_angle: Optional[float] = None
        self.firing_strength: Optional[float] = None

    def find_nearest_enemy(self, controlled: characters.Character) -> characters.Character | None:
        """Identifies the nearest enemy to the character.

        Args:
            controlled: The character which the team's AI is presently controlling.

        Returns:
            The nearest character to the controlled character, or None if no character is found.
        """
        nearest_enemy = None
        nearest_enemy_dist = 0.0

        for character in self.team.pf.characters:
            if character.health.alive and character.details.team is not self.team:
                new_enemy_dist = np.linalg.norm(
                    character.kinematics.pos - controlled.kinematics.pos
                )

                if not nearest_enemy or nearest_enemy_dist > new_enemy_dist:
                    nearest_enemy = character
                    nearest_enemy_dist = new_enemy_dist

        self.targeting_character = nearest_enemy

        # Faces the controlled character towards the target.
        if self.targeting_character is not None:
            controlled.facing_r = self.targeting_character.kinematics.x > controlled.kinematics.x

        return nearest_enemy_dist

    def scan_attacks(self) -> tuple[bool, float, float]:
        """Checks various options of attack."""
        controlled = self.team.pf.controlled_character

        best_damage = 0.0
        best_distance = 100000
        should_face_l = controlled.facing_l
        best_angle = (settings.MAXIMUM_FIRING_ANGLE + settings.MINIMUM_FIRING_ANGLE) / 2
        best_strength = settings.MAXIMUM_FIRING_POWER // 2

        for facing_l in (True, False):
            for angle in np.linspace(
                settings.MINIMUM_FIRING_ANGLE, settings.MAXIMUM_FIRING_ANGLE, 10
            ):
                for strength in np.linspace(0, settings.MAXIMUM_FIRING_POWER, 10):
                    attack_array = controlled.angle_array(angle, facing_l) * strength
                    projectile = Rocket(
                        self.team.pf,
                        (controlled.kinematics.x, controlled.kinematics.y),
                        (float(attack_array[0]), float(attack_array[1])),
                        controlled,
                    )
                    damage, distance = projectile.phantom(self.targeting_character)
                    if damage > best_damage or (damage == best_damage and distance < best_distance):
                        should_face_l = facing_l
                        best_damage = damage
                        best_distance = distance
                        best_angle = angle
                        best_strength = strength

        return should_face_l, best_angle, best_strength

    def run_ai(self, controlled: world_objects.Character) -> None:
        """Operates the AI for the team.

        Args:
            controlled: The character which the team's AI is presently controlling.
        """
        if not self.team.pf.game_state.controlled_can_attack:
            return

        if self.targeting_character is None:
            self.find_nearest_enemy(controlled)

        if self.targeting_character is not None:
            assert self.targeting_character.health.alive

        if not self.time_to_act and self.team.pf.time_left_on_clock() < 5:
            self.time_to_act = True

        if self.time_to_act and self.firing_angle is None:
            self.is_firing_left, self.firing_angle, self.firing_strength = self.scan_attacks()

        controlled.facing_l = self.is_firing_left

        if controlled.control.firing_angle < self.firing_angle:
            controlled.aim_upwards(self.firing_angle)

        elif controlled.control.firing_angle > self.firing_angle:
            controlled.aim_downwards(self.firing_angle)

        elif not controlled.control.preparing_attack:
            controlled.start_attack()

        elif controlled.control.firing_strength < self.firing_strength:
            controlled.prepare_attack(self.firing_strength)

        else:
            controlled.release_attack()
            self.is_firing_left = None
            self.firing_angle = None
            self.firing_strength = None
            self.targeting_character = None


class Team:
    """A team of allied characters.

    Attributes:
        pf: The playing field in which the team fights.
        team_number: An integer unique to the team amongst all teams on the playing field.
        characters: A list of all characters in the team.
        character_queue: A generator which continually provides the next character to be controlled
            from the team.
        ai: The AI acting on the team, if there is one, otherwise None.
    """

    teams: list[Team] = []
    """A complete list of all teams."""

    def __init__(self, pf: playing_field.PlayingField, has_ai: bool = False) -> None:
        """Creates the team according to the provided parameters.

        Args:
            pf: The playing field in which the team fights.
            has_ai: Whether or not the team is controlled by an AI.
        """
        self.pf: playing_field.PlayingField = pf
        self.team_number: int = len(Team.teams) + 1
        self.characters: list[characters.Character] = []
        self.teams.append(self)
        self.character_queue: Generator[characters.Character, None, None] = self.next_character()
        self.ai: Optional[Computer] = self.get_ai(has_ai)

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

    def next_character(self) -> Generator[world_objects.Character, None, None]:
        """Continuously cycles over the living characters.

        Yields:
            The next character available to play.
        """
        while True:
            for character in self.characters.copy():
                if character.health.alive:
                    yield character

    def add_character(self, x: int, y: int, name: str) -> world_objects.Character:
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
