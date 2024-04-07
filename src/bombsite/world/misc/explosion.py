"""explosion.py handles the effect of explosions on the environment.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

from bombsite.world import logger

if TYPE_CHECKING:
    from bombsite.world.characters import characters
    from bombsite.world.projectiles.projectiles import Projectile


def check_character_caught_by_explosion(
    pos: npt.NDArray[np.double],
    character: characters.Character,
    caused_by: characters.Character,
    radius: int = 40,
) -> None:
    """Checks if an explosion to damage the nearby terrain and characters.

    Args:
        pos: The source location of the explosion.
        character: The character being affected by the explosion.
        caused_by: The character who initiated the explosion.
        radius: The radius of the blast.
    """
    # Finds the distance from the blast of the character.
    vector = character.kinematics.pos - pos
    distance = float(np.linalg.norm(vector))

    # Only affects the character if sufficiently close.
    if distance < radius:
        # Creates a direction in which the character is flung,
        # complete with upwards momentum.
        blast_vector = vector + np.array((0, -25))
        blast_direction = blast_vector / np.linalg.norm(blast_vector)

        # Flings the character and causes them damage.
        character_caught_by_explosion(character, caused_by, blast_direction, distance, radius)


def character_caught_by_explosion(
    character: characters.Character,
    caused_by: characters.Character,
    blast_direction: npt.NDArray[np.double],
    distance: float,
    radius: int = 40,
):
    """Causes an explosion to damage the nearby terrain and characters.

    Args:
        character: The character being affected by the explosion.
        caused_by: The character who initiated the explosion.
        blast_direction: The array indicating the direction in which the character is to be thrown.
        distance: The distance of the character from the explosion.
        radius: The radius of the blast.
    """
    # Damages the character depending on how close the
    # explosion was.
    character.health.hp -= radius - int(distance)

    # Kills the character if it runs out of health.
    if character.health.hp <= 0:
        character.health.alive = False
        character.kinematics.null_velocity()

        # Sends a message depending on who killed the
        # character.
        if caused_by is character:
            logger.logger.log(f"{caused_by} has committed seppuku!")
        elif caused_by.details.team == character.details.team:
            logger.logger.log(f"{caused_by} accidentally killed {character}!")
        else:
            logger.logger.log(f"{caused_by} killed {character}!")

    # Flings the character in the appropriate direction.
    else:
        character.kinematics.vel += (blast_direction * (radius - distance)) * 0.1


def estimate_explosion_damage(projectile: Projectile) -> int:
    """Calculates how much damage an explosion would cause.

    This is calculated from the perspective of the projectile's sender, which means damage to their
    side is counted against them.

    Args:
        projectile: The projectile for which the explosion damage is being calculated.

    Returns:
        The net damage calculated by adding all damage to enemies and subtracting all damage to
        allies.
    """
    # Assumes no damage is caused initially.
    net_damage = 0

    # Iterates over each living character.
    for character in projectile.pf.alive_characters():
        # Finds the distance from the blast of the character.
        vector = character.kinematics.pos - projectile.kinematics.pos
        distance = np.linalg.norm(vector)

        # Only affects the character if sufficiently close.
        if distance < projectile.explosion_radius():
            damage = int(projectile.explosion_radius() - distance)
            if character.details.team is projectile.sent_by.details.team:
                net_damage -= min((damage, character.health.hp))
            else:
                net_damage += min((damage, character.health.hp))

    return net_damage
