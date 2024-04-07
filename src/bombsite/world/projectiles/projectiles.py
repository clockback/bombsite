"""projectiles.py is the module providing the projectiles that are shot by characters.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from bombsite.world.world_objects import WorldObject

if TYPE_CHECKING:
    from bombsite.world import playing_field
    from bombsite.world.characters.characters import Character


class Projectile(WorldObject):
    """A projectile that can damage characters.

    Attributes:
        sent_by: The character that launched the projectile.
    """

    def __init__(
        self,
        pf: playing_field.PlayingField,
        position: tuple[float, float],
        velocity: tuple[float, float],
        sent_by: Character,
    ) -> None:
        """Creates the projectile using the provided parameters.

        Args:
            pf: The playing field in which the object is placed.
            position: The x and y coordinates for the position of the projectile.
            velocity: The x and y components of the velocity of the projectile.
            sent_by: The character firing the projectile.
        """
        super().__init__(pf, position, velocity)
        self.sent_by: Character = sent_by

    @abc.abstractmethod
    def update(self) -> None:
        """Change's the projectile's attributes."""

    def visible(self) -> bool:
        """Determines whether or not the projectile is visible.

        Returns:
            Projectile visibility. This is always True.
        """
        return True

    def destroy(self) -> None:
        """Removes the projectile."""
        self.pf.world_objects.remove(self)

    @abc.abstractmethod
    def phantom(self, target: Character) -> tuple[int, float]:
        """Estimates the expected result of the projectile.

        Args:
            target: The character that the phantom projectile is attempting to reach.

        Returns: A tuple containing the expected damage from the attack, and the distance from the
            targeted character.
        """

    @abc.abstractmethod
    def explosion_radius(self) -> int:
        """The blast radius of the explosion caused by the projectile.

        Returns:
            The radius in pixels of the projectiles' explosion.
        """
        raise NotImplementedError
