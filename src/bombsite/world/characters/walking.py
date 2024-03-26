"""walking.py is the module providing defining the different values for a character walking.

Copyright © 2024 - Elliot Simpson
"""

from enum import Enum


class Walking(Enum):
    """An enum for the direction in which the character is walking."""

    NA = 1
    """The character is not walking."""

    LEFT = 2
    """The character is walking to the left."""

    RIGHT = 3
    """The character is walking to the right."""
