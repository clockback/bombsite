"""battleplan.py provides a plan for a character to launch a projectile.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bombsite.world.attacks.attack import Attack


@dataclass
class BattlePlan:
    """Contains a collection of attributes that an AI uses in launching an attack."""

    is_firing_left: bool
    """Whether or not the character should fire to the left."""

    firing_angle: float
    """The angle at which the character should fire."""

    firing_strength: float
    """The strength with which the projectile should be fired."""

    expected_damage: int
    """The amount of damage that the AI estimates will occur as a result of the attack."""

    expected_distance: float
    """The expected distance of the attack from the targetted character."""

    weapon_used: Attack
    """The weapon used in the assault."""
