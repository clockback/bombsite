"""world_objects.py is the module providing the objects that appear on the playing field.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt

if TYPE_CHECKING:
    import bombsite.display
    from bombsite.world import playing_field


@dataclass
class Kinematics:
    """The attribute of a world object relating to motion."""

    pos: npt.NDArray[np.double]
    """The x and y coordinates of the world object."""

    vel: npt.NDArray[np.double]
    """The x and y components of the world object's velocity."""

    @property
    def x(self) -> float:
        """The getter for the x-component of the object's position.

        Returns:
            The world object's floating-point-value x-position.
        """
        return float(self.pos[0])

    @x.setter
    def x(self, value: float) -> None:
        """The setter for the x-component of the object's position.

        Args:
            value: The new world object's x-position.
        """
        self.pos[0] = value

    @property
    def y(self) -> float:
        """The getter for the y-component of the object's position.

        Returns:
            The world object's floating-point-value y-position.
        """
        return float(self.pos[1])

    @y.setter
    def y(self, value: float) -> None:
        """The setter for the y-component of the object's position.

        Args:
            value: The new world object's x-position.
        """
        self.pos[1] = value

    @property
    def vx(self) -> float:
        """The getter for the x-component of the object's velocity.

        Returns:
            The world object's floating-point-value x-velocity.
        """
        return float(self.vel[0])

    @vx.setter
    def vx(self, value: float) -> None:
        """The setter for the x-component of the object's velocity.

        Args:
            value: The new world object's x-velocity.
        """
        self.vel[0] = value

    @property
    def vy(self) -> float:
        """The getter for the y-component of the object's velocity.

        Returns:
            The world object's floating-point-value y-velocity.
        """
        return float(self.vel[1])

    @vy.setter
    def vy(self, value: float) -> None:
        """The setter for the y-component of the object's velocity.

        Args:
            value: The new world object's y-velocity.
        """
        self.vel[1] = value

    @property
    def intpos(self) -> tuple[int, int]:
        """The getter for the integer-position of the object.

        Returns:
            A tuple with the integer values for the x and y position of the object.
        """
        return int(self.x), int(self.y)


class WorldObject(abc.ABC):
    """Any world object on the playing field.

    Attributes:
        pf: The playing field in which the object is placed.
        kinematics: The motion-related attributes of the object.
    """

    def __init__(
        self,
        pf: playing_field.PlayingField,
        position: tuple[float, float],
        velocity: tuple[float, float] = (0.0, 0.0),
    ) -> None:
        """Creates the world object using the provided parameters.

        Args:
            pf: The playing field in which the object is placed.
            position: The x and y coordinates of the object.
            velocity: The x and y velocity components of the object.
        """
        self.pf: playing_field.PlayingField = pf
        self.kinematics: Kinematics = Kinematics(
            pos=np.array(position, dtype=np.double), vel=np.array(velocity, dtype=np.double)
        )

    def debug_show_position(self, r: int = 3) -> None:
        """Displays the map area surrounding the character.

        Args:
            r: The radius around the character to be displayed.
        """
        x_slice = slice(int(self.kinematics.x) - r + 1, int(self.kinematics.x) + r)
        y_slice = slice(int(self.kinematics.y) - r + 1, int(self.kinematics.y) + r)
        section = self.pf.mask[x_slice, y_slice]
        for row in section.transpose():
            print("".join("X" if mask_value else "." for mask_value in row))

    @abc.abstractmethod
    def update(self) -> None:
        """The abstract method that is run every tick for the world object."""

    @abc.abstractmethod
    def visible(self) -> bool:
        """The abstract method that returns whether or not the object should be displayed.

        Returns:
            True if the renderer should display the object on the screen, otherwise False.
        """

    def apply_gravity(self) -> None:
        """Accelerates the object downwards."""
        self.kinematics.vy += 0.05

    @abc.abstractmethod
    def draw(self, display: bombsite.display.Display) -> None:
        """Draws the world object onto the playing field.

        Args:
            display: The display onto which the character is to be drawn.
        """

    def null_velocity(self) -> None:
        """Sets the world object's velocity components to zero."""
        self.kinematics.vx = 0.0
        self.kinematics.vy = 0.0

    def set_vx(self, vx: float) -> None:
        """Sets the new value for the horizontal velocity of the world object.

        Args:
            vx: The floating point value for the horizontal velocity of the world object.
        """
        self.kinematics.vx = vx

    def set_vy(self, vy: float) -> None:
        """Sets the new value for the vertical velocity of the world object.

        Args:
            vy: The floating point value for the vertical velocity of the world object.
        """
        self.kinematics.vy = vy

    def set_pos(self, pos: npt.NDArray[np.double | np.int64]) -> None:
        """Sets new values for the x and y components of the world object.

        Args:
            pos: The position of the world object.
        """
        self.kinematics.pos = pos.astype(float)
