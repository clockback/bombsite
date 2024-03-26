"""projectiles.py is the module providing the projectiles that are shot by characters.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

import numpy as np
import pygame

from bombsite.world.world_objects import WorldObject

if TYPE_CHECKING:
    import bombsite.display
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
        """
        super().__init__(pf, position, velocity)
        self.sent_by: Character = sent_by

    def update(self) -> None:
        """Change's the projectile's attributes."""
        # Destroys the projectile if it leaves the map.
        if (
            self.kinematics.x < 0
            or self.kinematics.x > self.pf.mask.shape[0]
            or self.kinematics.y > self.pf.mask.shape[1]
        ):
            self.destroy()
            return

        # Causes the projectile to fall.
        self.apply_gravity()
        self.set_pos(self.kinematics.pos + self.kinematics.vel)

        # Detonates the projectile if it collides with the terrain.
        if self.pf.collision_pixel(*self.kinematics.pos):
            self.pf.explosion(self.kinematics.pos, self.sent_by, self.explosion_radius())
            self.destroy()

    def visible(self) -> bool:
        """Determines whether or not the projectile is visible.

        Returns:
            Projectile visibility. This is always True.
        """
        return True

    def destroy(self) -> None:
        """Removes the projectile."""
        self.pf.world_objects.remove(self)

    def phantom(self, target: Character) -> tuple[int, int]:
        """Estimates the expected result of the projectile.

        Args:
            target: The character that the phantom projectile is attempting to reach.

        Returns: A tuple containing the expected damage from the attack, and the distance from the
            targeted character.
        """
        net_damage = 0

        while True:
            self.apply_gravity()
            self.set_pos(self.kinematics.pos + self.kinematics.vel)

            # Destroys the projectile if it leaves the map.
            if (
                self.kinematics.x < 0
                or self.kinematics.x > self.pf.mask.shape[0]
                or self.kinematics.y > self.pf.mask.shape[1]
            ):
                return net_damage, np.linalg.norm(self.kinematics.pos - target.kinematics.pos)

            if self.pf.collision_pixel(*self.kinematics.pos):
                # Affects nearby characters caught in the blast.
                for character in self.pf.alive_characters():
                    # Finds the distance from the blast of the character.
                    vector = character.kinematics.pos - self.kinematics.pos
                    distance = np.linalg.norm(vector)

                    # Only affects the character if sufficiently close.
                    if distance < self.explosion_radius():
                        damage = int(self.explosion_radius() - distance)
                        if character.details.team is self.sent_by.details.team:
                            net_damage -= min((damage, character.health.hp))
                        else:
                            net_damage += min((damage, character.health.hp))

                break

        return net_damage, np.linalg.norm(self.kinematics.pos - target.kinematics.pos)

    def draw(self, display: bombsite.display.Display) -> None:
        """Draws the projectile onto the playing field.

        Args:
            display: The display onto which the character is to be drawn.
        """
        pygame.draw.circle(
            display.screen, pygame.Color("black"), self.kinematics.pos - display.pos, 2
        )

    @abc.abstractmethod
    def explosion_radius(self) -> int:
        """The blast radius of the explosion caused by the projectile.

        Returns:
            The radius in pixels of the projectiles' explosion.
        """
        raise NotImplementedError
