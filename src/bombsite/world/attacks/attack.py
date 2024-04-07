"""attack.py provides a base class for all means of attack.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from bombsite.world.characters.characters import Character


@dataclass
class AttackOverride:
    """The description of the attack the character must launch."""

    leftwards: bool = True
    """True if the character should attack leftwards. Otherwise False."""

    angle: int = 0
    """The angle at which the character must attack. An angle of zero is horizontal."""

    power: float = 0
    """The power with which a projectile should be launched/fired."""


class Attack(metaclass=abc.ABCMeta):
    """An attack with interfaces for what projectiles, etc. it releases."""

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """Returns the name of the character.

        Returns:
            The name of the attack.
        """

    @classmethod
    @abc.abstractmethod
    def image(cls) -> pygame.Surface:
        """Returns the image for the attack.

        Returns:
            The image for the attack used in the attack selector.
        """

    @abc.abstractmethod
    def release(self, launcher: Character) -> None:
        """Releases the attack.

        Args:
            launcher: The character launching the attack.
        """

    @abc.abstractmethod
    def release_phantom(
        self, launcher: Character, attack_override: AttackOverride
    ) -> tuple[int, float]:
        """Releases the attack as a phantom.

        Args:
            launcher: The character launching the attack.
            attack_override: The attack information for the projectile. If using the character's
                settings, this is None.

        Returns:
            A tuple containing the expected total damage from the attack, and the distance from the
            targeted character.
        """
