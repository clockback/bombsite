"""battleplan.py provides a plan for a character to launch a projectile.

Copyright © 2024 - Elliot Simpson
"""

from dataclasses import dataclass


@dataclass
class BattlePlan:
    """Contains a collection of attributes that an AI uses in launching an attack."""

    is_firing_left: bool
    """Whether or not the character should fire to the left."""

    firing_angle: float
    """The angle at which the character should fire."""

    firing_strength: float
    """The strength with which the projectile should be fired."""
