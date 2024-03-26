"""details.py is the module giving metadata regarding who the character is.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bombsite.world.teams import Team


@dataclass
class Details:
    """A collection of attributes specific to who a character is."""

    name: str
    """The name of the character."""

    team: Team
    """The team to which the character belongs."""
