"""computer.py provides an artificial intelligence for a computer-controlled team.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from collections.abc import Generator
from itertools import product
from typing import TYPE_CHECKING

import numpy as np

from bombsite import settings
from bombsite.ui.attackselector import AttackSelector
from bombsite.world.attacks.attack import AttackOverride
from bombsite.world.teams.battleplan import BattlePlan

if TYPE_CHECKING:
    from bombsite.world.attacks.attack import Attack
    from bombsite.world.characters.characters import Character
    from bombsite.world.teams.teams import Team


class Computer:
    """A computer AI which can issue commands to the characters.

    Attributes:
        team: The team the AI applies to.
        battleplan_generator: A generator which iterates through every attack type and finds the
            best course of action.
        battleplan: The best course of action yet found via battleplan_generator.
        _targeting_character: The character that the AI has most recently decided to attack.
    """

    def __init__(self, team: Team) -> None:
        """Creates the computer according to the provided parameters.

        Args:
            team: The team which has the computer AI.
        """
        self.team: Team = team
        self.battleplan_generator: Generator[BattlePlan, None, None] | None = None
        self.battleplan: BattlePlan | None = None
        self._targeting_character: Character | None = None

    @property
    def targeting_character_or_none(self) -> Character | None:
        """Returns whichever character the AI is presently targeting.

        Returns:
            The character which the AI is attempting to fire at. This is not strict, and is to help
            the AI fire as close as it can to an enemy, even when it does not strike the enemy.
        """
        return self._targeting_character

    @property
    def targeting_character(self) -> Character:
        """Returns whichever character the AI is presently targeting.

        Returns:
            The character which the AI is attempting to fire at. This is not strict, and is to help
            the AI fire as close as it can to an enemy, even when it does not strike the enemy.

        Raises:
            ValueError: The AI is not targeting anyone.
        """
        character = self.targeting_character_or_none

        if character is None:
            raise ValueError("No targeting charactering found.")

        return character

    def _set_targeting_character(self, character: Character | None) -> None:
        """Sets the character which the AI is targeting.

        Args:
            character: The new character the AI is going to target.
        """
        self._targeting_character = character

    def find_nearest_enemy(self, controlled: Character) -> None:
        """Identifies the nearest enemy to the character.

        Args:
            controlled: The character which the team's AI is presently controlling.
        """
        nearest_enemy = None
        nearest_enemy_dist = 0.0

        for character in self.team.pf.characters:
            if character.details.team is self.team or not character.health.alive:
                continue

            new_enemy_dist = np.linalg.norm(character.kinematics.pos - controlled.kinematics.pos)

            if not nearest_enemy or nearest_enemy_dist > new_enemy_dist:
                nearest_enemy = character
                nearest_enemy_dist = float(new_enemy_dist)

        # Faces the controlled character towards the target.
        if nearest_enemy is not None:
            controlled.facing_r = nearest_enemy.kinematics.x > controlled.kinematics.x

        self._set_targeting_character(nearest_enemy)

    def scan_attacks(self, attack_type: type[Attack]) -> BattlePlan:
        """Checks various options of attack.

        Args:
            attack_type: The type of attack to use in the battle plan.

        Returns:
            A plan of attack containing the direction that the character should face, the angle at
            which it should fire, and the strength with which should fire.
        """
        controlled = self.team.pf.controlled_character

        attack = attack_type()

        best_damage = 0
        best_distance = 100000.0
        should_face_l = controlled.facing_l
        best_angle = (settings.MAXIMUM_FIRING_ANGLE + settings.MINIMUM_FIRING_ANGLE) / 2
        best_strength = settings.MAXIMUM_FIRING_POWER // 2

        for facing_l, angle, strength in product(
            (True, False),
            np.linspace(settings.MINIMUM_FIRING_ANGLE, settings.MAXIMUM_FIRING_ANGLE, 10),
            np.linspace(0, settings.MAXIMUM_FIRING_POWER),
        ):
            attack_override = AttackOverride(facing_l, angle, strength)
            damage, distance = attack.release_phantom(controlled, attack_override)
            if damage > best_damage or (damage == best_damage and distance < best_distance):
                should_face_l = facing_l
                best_damage = damage
                best_distance = distance
                best_angle = angle
                best_strength = strength

        return BattlePlan(
            should_face_l, best_angle, best_strength, best_damage, best_distance, attack
        )

    def run_ai(self, controlled: Character) -> None:
        """Operates the AI for the team.

        Args:
            controlled: The character which the team's AI is presently controlling.
        """
        if not self.team.pf.game_state.controlled_can_attack:
            return

        if self.targeting_character_or_none is None:
            self.find_nearest_enemy(controlled)

        battleplan = self._find_new_battleplans()
        if battleplan is None:
            return

        self.team.attack = battleplan.weapon_used
        controlled.facing_l = battleplan.is_firing_left

        if controlled.control.firing_angle < battleplan.firing_angle:
            controlled.aim_upwards(battleplan.firing_angle)

        elif controlled.control.firing_angle > battleplan.firing_angle:
            controlled.aim_downwards(battleplan.firing_angle)

        elif not controlled.control.preparing_attack:
            controlled.start_attack()

        elif controlled.control.firing_strength < battleplan.firing_strength:
            controlled.prepare_attack(battleplan.firing_strength)

        else:
            controlled.release_attack()
            self.battleplan = None
            self._set_targeting_character(None)

    def _find_new_battleplans(self) -> BattlePlan | None:
        """Attempts to search through possible battleplans.

        Returns:
            A finalized battleplan if one has been found.
        """
        # If a battleplan has not been found, and no battleplans have been searched, begins to look,
        # considering the first battleplan found the best so far.
        if self.battleplan is None and self.battleplan_generator is None:
            self.battleplan_generator = self.iterate_over_attack_plans()
            self.battleplan = next(self.battleplan_generator)
            return None

        # Raises an error if no battle plan is found, despite having looked.
        elif self.battleplan is None:
            raise ValueError("No battleplan found!")

        # If a battleplan is found, but there is no searching in process, it means the search is
        # already complete.
        elif self.battleplan_generator is None:
            return self.battleplan

        # Finds the next attack-optimized battleplan.
        try:
            new_battleplan = next(self.battleplan_generator)

        # If battleplans have been found, stops searching.
        except StopIteration:
            self.battleplan_generator = None
            return self.battleplan

        # Replaces the current battleplan if it is inferior to the newly found battleplan.
        if new_battleplan.expected_damage > self.battleplan.expected_damage or (
            new_battleplan.expected_damage == self.battleplan.expected_damage
            and new_battleplan.expected_distance < self.battleplan.expected_distance
        ):
            self.battleplan = new_battleplan

        return None

    def iterate_over_attack_plans(self) -> Generator[BattlePlan, None, None]:
        """Iterates over each attack and finds the best battle plan possible.

        Yields:
            The best battle plan for a given attack type.
        """
        yield from map(self.scan_attacks, AttackSelector.all_attacks())
