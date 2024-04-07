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

    def null_velocity(self) -> None:
        """Sets the world object's velocity components to zero."""
        self.vx = 0.0
        self.vy = 0.0


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

    def _surrounding_is(self, match: npt.NDArray[np.int_]) -> bool:
        """Checks if the mask around the character matches the template given.

        Args:
            match: A 3x3 array, centered on the character's position, with the expected values:
                * 0 for no ground.
                * 1 for ground.
                * -1 for either (does not matter which).

        Returns:
            Whether or not the mask and match correspond.

        Raises:
            ValueError: The provided array is not the right shape.
        """
        # Raises an error for a malformed match array.
        if match.shape != (3, 3):
            raise ValueError(f"Expected array with dimensions (3, 3). Got {match.shape}.")

        # Obtains the part of the mask around the character, using clipping to prevent index errors
        # when the character is outside the map boundaries.
        x, y = self.kinematics.pos.astype(int)
        cols = self.pf.mask.take(range(x - 1, x + 2), axis=0, mode="clip")
        section = cols.take(range(y - 1, y + 2), axis=1, mode="clip").transpose()

        # An error only occurs where the sum of the mask and match at a position is equal to 1,
        # which only happens when one value is 0 and another value is 1, meaning that whatever
        # value checked in the match is not in the mask.
        return 1 not in (match + section)

    @property
    def _bounce_halting_speed(self) -> float:
        """Returns the speed below which all bounces must not happen.

        Returns:
            A value indicating the total speed below which bouncing stops.
        """
        return NotImplemented

    @property
    def _bounce_factor(self) -> float:
        """A bounce factor. The higher the factor, the greater the bounce.

        Returns:
            A value indicating how elastically the world object bounces.
        """
        return NotImplemented

    def _bounce_given_factor(self, ratio_x: float, ratio_y: float) -> None:
        """Modifies the existing velocity to bounce.

        Args:
            ratio_x: The effect the bounce has on the x-velocity component.
            ratio_y: The effect the bounce has on the y-velocity component.
        """
        self.set_vx(ratio_x * self._bounce_factor)
        self.set_vy(ratio_y * self._bounce_factor)

    def _bounce(self) -> None:
        """Bounces off whatever surface the character hit."""
        # Does not bounce if not fast enough.
        if np.linalg.norm(self.kinematics.vel) <= self._bounce_halting_speed:
            self.kinematics.null_velocity()

        # Bounces if the ground is flat.
        elif self._surrounding_is(np.array(((0, 0, 0), (0, 0, 0), (1, 1, 1)))):
            self._bounce_given_factor(0.8 * self.kinematics.vx, -0.4 * self.kinematics.vy)

        # Bounces if the ground is sloped downwards to the right.
        elif self._surrounding_is(np.array(((0, 0, 0), (1, 0, 0), (-1, 1, -1)))):
            self._bounce_given_factor(0.6 * self.kinematics.vy, 0.6 * self.kinematics.vx)

        # Bounces if the ground is sloped downwards to the left.
        elif self._surrounding_is(np.array(((0, 0, 0), (0, 0, 1), (-1, 1, -1)))):
            self._bounce_given_factor(-0.6 * self.kinematics.vy, -0.6 * self.kinematics.vx)

        # If the ground is too unpredictable, the character stops falling.
        else:
            self.kinematics.null_velocity()

    def _will_collide(self) -> bool:
        """Detects if a collision will occur due to the world object's movement.

        Returns:
            True if a collision has occurred, otherwise false.
        """
        return self.pf.collision_pixel(*(self.kinematics.pos + self.kinematics.vel).astype(int))

    def _collide(self) -> None:
        """Enacts a collision with the playing field."""
        raise NotImplementedError

    def _update_position(self, check_collision: bool = True) -> None:
        """Updates the position of the world object, checking for collision if necessary.

        Args:
            check_collision: Whether or not to check for collision.
        """
        if check_collision and self._will_collide():
            self._collide()
        else:
            self.set_pos(self.kinematics.pos + self.kinematics.vel)

    @abc.abstractmethod
    def is_in_steady_state(self) -> bool:
        """Determines whether or not the world object is going to remain still without provocation.

        Returns:
            True if the world object will remain still without provocation, False if it is moving
            or could cause motion later.
        """

    def _exited_playing_field(self) -> bool:
        """Determines whether or not the world object is still in the playing field area.

        Returns:
            True if the world object is still in the playing field, False otherwise.
        """
        return (
            self.kinematics.x < 0
            or self.kinematics.x > self.pf.mask.shape[0]
            or self.kinematics.y > self.pf.mask.shape[1]
        )
