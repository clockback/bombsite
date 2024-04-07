"""rocketlauncher.py defines a rocket launcher attack which, as the name suggests, launches rockets.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
import pygame

from bombsite.utils import images_path
from bombsite.world.attacks.attack import Attack
from bombsite.world.projectiles.rocket import Rocket

if TYPE_CHECKING:
    from bombsite.world.attacks.attack import AttackOverride
    from bombsite.world.characters.characters import Character


class RocketLauncher(Attack):
    """An attack with interfaces for the rockets it releases."""

    _image = pygame.image.load(images_path / "attacks" / "rocketlauncher" / "rocketlauncher.png")
    """The image for the rocket launcher itself."""

    @classmethod
    def name(cls) -> str:
        """Returns the name of the attack.

        Returns:
            The string "Rocket launcher".
        """
        return "Rocket launcher"

    @classmethod
    def image(cls) -> pygame.Surface:
        """Returns the image for the attack.

        Returns:
            The image for the attack used in the attack selector.
        """
        return cls._image

    def _create_rocket(self, launcher: Character, projectile_vel: npt.NDArray[np.double]) -> Rocket:
        """Creates a rocket.

        Args:
            launcher: The character launching the rocket.
            projectile_vel: The array indicating the velocity of the rocket.

        Returns:
            The rocket instance.
        """
        return Rocket(
            launcher.details.team.pf,
            (launcher.kinematics.x, launcher.kinematics.y),
            (float(projectile_vel[0]), float(projectile_vel[1])),
            launcher,
        )

    def release(self, launcher: Character) -> None:
        """Releases the attack.

        Args:
            launcher: The character launching the attack.
        """
        # Determines the velocity of the rocket at launch.
        projectile_vel = launcher.angle_array() * launcher.control.firing_strength

        # Creates a rocket instance.
        rocket = self._create_rocket(launcher, projectile_vel)

        # Adds the rocket to the world.
        launcher.pf.world_objects.append(rocket)

    def release_phantom(
        self, launcher: Character, attack_override: AttackOverride
    ) -> tuple[int, float]:
        """Releases the attack as a phantom.

        Args:
            launcher: The character launching the attack.
            attack_override: The attack information for the rocket. If using the character's
                settings, this is None.

        Returns:
            A tuple containing the expected total damage from the attack, and the distance from the
            targeted character.
        """
        # Determines the velocity of the rocket at launch.
        projectile_vel = (
            launcher.angle_array(attack_override.angle, attack_override.leftwards)
            * attack_override.power
        )

        # Creates a rocket instance.
        return self._create_rocket(launcher, projectile_vel).phantom(launcher)
