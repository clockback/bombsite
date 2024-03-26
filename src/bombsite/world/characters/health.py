"""health.py is the module providing the health of the game's characters.

Copyright © 2024 - Elliot Simpson
"""

from dataclasses import dataclass


@dataclass
class Health:
    """Contains the individual attributes relating to the healthiness of a character."""

    hp: int = 100
    """The hit points of the character."""

    alive: bool = True
    """Whether or not the character is alive."""
