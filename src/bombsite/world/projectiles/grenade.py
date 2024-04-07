"""grenade.py provides the most basic form of attack.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pygame

from bombsite.settings import GRENADE_BLAST_RADIUS
from bombsite.world.misc.explosion import estimate_explosion_damage

from . import projectiles

if TYPE_CHECKING:
    from bombsite.display import Display
    from bombsite.world.characters.characters import Character
    from bombsite.world.playing_field import PlayingField


class Grenade(projectiles.Projectile):
    """The grenade bounces about for a while before exploding, damaging the surrounding area.

    Attributes:
        frames_left: The number of frames left before the grenade detonates.
    """

    def __init__(
        self,
        pf: PlayingField,
        position: tuple[float, float],
        velocity: tuple[float, float],
        sent_by: Character,
    ) -> None:
        """Sets the duration of time left before the grenade explodes.

        Args:
            pf: The playing field in which the grenade is placed.
            position: The x and y coordinates for the position of the grenade.
            velocity: The x and y components of the velocity of the grenade.
            sent_by: The character launching the grenade.
        """
        super().__init__(pf, position, velocity, sent_by)
        self.frames_left: int = 400

    def explosion_radius(self) -> int:
        """The blast radius of the explosion caused by a grenade.

        Returns:
            The radius in pixels of the grenade's explosion.
        """
        return GRENADE_BLAST_RADIUS

    def update(self) -> None:
        """Change's the grenade's attributes."""
        # Destroys the grenade if it leaves the map.
        if self._exited_playing_field():
            self.destroy()
            return

        # Checks if the grenade should explode.
        if self.frames_left <= 0:
            self.pf.explosion(self.kinematics.pos, self.sent_by, self.explosion_radius())
            self.destroy()

        self.apply_gravity()
        self._update_position()

        # Runs the fuse on how long the grenade has left to explode.
        self.frames_left -= 1

    def _collide(self) -> None:
        """Enacts a collision with the playing field."""
        lower_bound = self.kinematics.pos.astype(int)

        if not self.pf.collision_pixel(*lower_bound):
            upper_bound = (self.kinematics.pos + self.kinematics.vel).astype(int)
            self.set_pos(self.pf.find_collision_point(lower_bound, upper_bound))

        self._bounce()

    def phantom(self, target: Character) -> tuple[int, float]:
        """Estimates the expected result of the grenade.

        Args:
            target: The character that the grenade is attempting to reach.

        Returns: A tuple containing the expected damage from the attack, and the distance from the
            targeted character.
        """
        while True:
            # Checks if the grenade should explode.
            if self.frames_left <= 0:
                distance = float(np.linalg.norm(self.kinematics.pos - target.kinematics.pos))
                return estimate_explosion_damage(self), distance

            # Destroys the grenade if it leaves the map.
            if self._exited_playing_field():
                return 0, float(np.linalg.norm(self.kinematics.pos - target.kinematics.pos))

            # Causes the grenade to fall.
            self.apply_gravity()
            if self._will_collide():
                self._collide()
            else:
                self.set_pos(self.kinematics.pos + self.kinematics.vel)

            # Runs the fuse on how long the grenade has left to explode.
            self.frames_left -= 1

    @property
    def _bounce_halting_speed(self) -> float:
        """Returns the speed below which all bounces must not happen.

        Returns:
            A value indicating the total speed below which bouncing stops.
        """
        return 1.0

    @property
    def _bounce_factor(self) -> float:
        """A bounce factor. The higher the factor, the greater the bounce.

        Returns:
            A value indicating how elastically the character bounces.
        """
        return 0.9

    def is_in_steady_state(self) -> bool:
        """Determines whether or not the world object is going to remain still without provocation.

        Returns:
            True if the world object will remain still without provocation, False if it is moving
            or could cause motion later.
        """
        return False

    def draw(self, display: Display) -> None:
        """Draws the grenade onto the playing field.

        Args:
            display: The display onto which the grenade is to be drawn.
        """
        draw_x, draw_y = self.kinematics.pos - display.pos
        pygame.draw.circle(display.screen, pygame.Color("darkolivegreen"), (draw_x, draw_y), 2)
