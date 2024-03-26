"""control.py is the module providing a team control over a user.

Copyright © 2024 - Elliot Simpson
"""

from dataclasses import dataclass

from bombsite.world.characters.walking import Walking


@dataclass
class Control:
    """A collection of attributes specific to a character's control."""

    controlled: bool = False
    """Whether or not the character is being controlled."""

    walking: Walking = Walking.NA
    """The direction in which the character is walking, if applicable."""

    preparing_attack: bool = False
    """Whether or not the character is preparing an attack."""

    firing_angle: int = 30
    """The angle at which the character is aiming."""

    firing_strength: float = 0.0
    """The speed with which the character is going to launch a projectile."""
