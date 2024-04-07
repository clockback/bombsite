"""throwgrenade.py hurls a timed grenade.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from bombsite.utils import images_path
from bombsite.world.attacks.attack import Attack
from bombsite.world.projectiles.grenade import Grenade

if TYPE_CHECKING:
    from bombsite.world.attacks.attack import AttackOverride
    from bombsite.world.characters.characters import Character


class ThrowGrenade(Attack):
    """An attack with interfaces for the grenades it releases."""

    _image = pygame.image.load(images_path / "attacks" / "throwgrenade" / "throwgrenade.png")
    """The image for the grenade itself."""

    @classmethod
    def name(cls) -> str:
        """Returns the name of the attack.

        Returns:
            The string "Grenade".
        """
        return "Grenade"

    @classmethod
    def image(cls) -> pygame.Surface:
        """Returns the image for the attack.

        Returns:
            The image for the attack used in the attack selector.
        """
        return cls._image

    def release(self, launcher: Character) -> None:
        """Releases the attack.

        Args:
            launcher: The character launching the attack.
        """
        # Determines the velocity of the grenade at launch.
        projectile_vel = launcher.angle_array() * launcher.control.firing_strength

        # Creates a grenade instance.
        grenade = Grenade(
            launcher.details.team.pf,
            (launcher.kinematics.x, launcher.kinematics.y),
            (float(projectile_vel[0]), float(projectile_vel[1])),
            launcher,
        )

        # Adds the grenade to the world.
        launcher.pf.world_objects.append(grenade)

    def release_phantom(
        self, launcher: Character, attack_override: AttackOverride
    ) -> tuple[int, float]:
        """Releases the attack as a phantom.

        Args:
            launcher: The character launching the attack.
            attack_override: The attack information for the grenade. If using the character's
                settings, this is None.

        Returns:
            A tuple containing the expected total damage from the attack, and the distance from the
            targeted character.
        """
        # Determines the velocity of the grenade at launch.
        grenade_vel = (
            launcher.angle_array(attack_override.angle, attack_override.leftwards)
            * attack_override.power
        )

        # Creates a grenade instance.
        return Grenade(
            launcher.details.team.pf,
            (launcher.kinematics.x, launcher.kinematics.y),
            (float(grenade_vel[0]), float(grenade_vel[1])),
            launcher,
        ).phantom(launcher)
