"""rocket.py provides the most basic form of attack.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pygame

from bombsite.settings import ROCKET_BLAST_RADIUS
from bombsite.world.misc.explosion import estimate_explosion_damage

from . import projectiles

if TYPE_CHECKING:
    from bombsite.display import Display
    from bombsite.world.characters.characters import Character


class Rocket(projectiles.Projectile):
    """The rocket which explodes immediately on contact, damaging the surrounding area."""

    def explosion_radius(self) -> int:
        """The blast radius of the explosion caused by a rocket.

        Returns:
            The radius in pixels of the rocket's explosion.
        """
        return ROCKET_BLAST_RADIUS

    def update(self) -> None:
        """Change's the rocket's attributes."""
        # Destroys the projectile if it leaves the map.
        if self._exited_playing_field():
            self.destroy()
            return

        # Causes the projectile to fall.
        self.apply_gravity()
        self._update_position(check_collision=False)

        # Detonates the projectile if it collides with the terrain.
        if self.pf.collision_pixel(*self.kinematics.pos):
            self.pf.explosion(self.kinematics.pos, self.sent_by, self.explosion_radius())
            self.destroy()

    def phantom(self, target: Character) -> tuple[int, float]:
        """Estimates the expected result of the rocket.

        Args:
            target: The character that the rocket projectile is attempting to reach.

        Returns: A tuple containing the expected damage from the attack, and the distance from the
            targeted character.
        """
        while True:
            self.apply_gravity()
            self.set_pos(self.kinematics.pos + self.kinematics.vel)

            # Destroys the projectile if it leaves the map.
            if self._exited_playing_field():
                return 0, float(np.linalg.norm(self.kinematics.pos - target.kinematics.pos))

            if self.pf.collision_pixel(*self.kinematics.pos):
                distance = float(np.linalg.norm(self.kinematics.pos - target.kinematics.pos))
                return estimate_explosion_damage(self), distance

    def is_in_steady_state(self) -> bool:
        """Determines whether or not the world object is going to remain still without provocation.

        Returns:
            True if the world object will remain still without provocation, False if it is moving
            or could cause motion later.
        """
        return False

    def draw(self, display: Display) -> None:
        """Draws the rocket onto the playing field.

        Args:
            display: The display onto which the rocket is to be drawn.
        """
        draw_x, draw_y = self.kinematics.pos - display.pos
        pygame.draw.circle(display.screen, pygame.Color("black"), (draw_x, draw_y), 2)
