"""rocket.py provides the most basic form of attack.

Copyright © 2024 - Elliot Simpson
"""

from bombsite.settings import ROCKET_BLAST_RADIUS

from . import projectiles


class Rocket(projectiles.Projectile):
    """The rocket which explodes immediately on contact, damaging the surrounding area."""

    def explosion_radius(self) -> int:
        """The blast radius of the explosion caused by a rocket.

        Returns:
            The radius in pixels of the rocket's explosion.
        """
        return ROCKET_BLAST_RADIUS
