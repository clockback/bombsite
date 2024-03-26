"""characters.py is the module providing the characters that fight one another.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

import numpy as np
import numpy.typing as npt
import pygame.key
from typing_extensions import Self

import bombsite.display
from bombsite import logger, settings
from bombsite.utils import package_path
from bombsite.world.characters.control import Control
from bombsite.world.characters.details import Details
from bombsite.world.characters.health import Health
from bombsite.world.characters.walking import Walking
from bombsite.world.projectiles.rocket import Rocket
from bombsite.world.world_objects import WorldObject

if TYPE_CHECKING:
    from bombsite.world import playing_field
    from bombsite.world.teams import Team


class Character(WorldObject):
    """A character that can move and attack.

    Attributes:
        details: The characteristics of the character relating to their affiliation.
        control: The attributes of the character relating to control by a team.
        _facing_l: Whether or not the character is facing to the left.
        health: The health the character.
    """

    font: pygame.font.Font = pygame.font.Font(
        package_path / "fonts" / "playpen_sans" / "PlaypenSans-Regular.ttf", 10
    )
    """The font used to render the names of the characters."""

    def __init__(
        self,
        pf: playing_field.PlayingField,
        pos: tuple[int, int],
        name: str,
        team: Team,
    ) -> None:
        """Creates the character using the provided parameters.

        Args:
            pf: The playing field in which the character exists.
            position: The x and y coordinates for the position of the character.
            name: The name of the character.
            team: The number team (starting from 1) in which the character is placed.
        """
        super().__init__(pf, pos, (0, 0))
        self.details: Details = Details(name, team)
        self.control: Control = Control()
        self._facing_l: bool = random.choice((True, False))
        self.health: Health = Health()

    def __str__(self) -> str:
        return self.details.name

    @property
    def facing_l(self) -> bool:
        """Returns whether or not the character is facing to the left.

        Returns:
            True if the character is facing to the left, otherwise False.
        """
        return self._facing_l

    @facing_l.setter
    def facing_l(self, value: bool) -> None:
        """Sets whether or not the character is facing to the left.

        Args:
            value: True if the character should face to the left, otherwise False.
        """
        self._facing_l = value

    @property
    def facing_r(self) -> bool:
        """Returns whether or not the character is facing to the right.

        Returns:
            True if the character is facing to the right, otherwise False.
        """
        return not self._facing_l

    @facing_r.setter
    def facing_r(self, value: bool) -> None:
        """Sets whether or not the character is facing to the right.

        Args:
            value: True if the character should face to the right, otherwise False.
        """
        self._facing_l = not value

    @property
    def _is_standing(self) -> bool:
        """Whether or not the character is standing on ground.

        Returns:
            Boolean for whether or not the character is standing on ground.
        """
        if not self.kinematics.vy:
            if self.pf.collision_pixel(self.kinematics.x, self.kinematics.y + 1):
                if not self.pf.collision_pixel(self.kinematics.x, self.kinematics.y):
                    return True

        return False

    @property
    def _moving_left(self) -> bool:
        """Whether or not the character is moving left.

        Returns:
            True if the character is either moving to the left, or is being commanded to walk to the
            left.
        """
        return self.kinematics.vx < 0 or self.control.walking == Walking.LEFT

    @property
    def _moving_right(self) -> bool:
        """Whether or not the character is moving right.

        Returns:
            True if the character is either moving to the right, or is being commanded to walk to
            the right.
        """
        return self.kinematics.vx > 0 or self.control.walking == Walking.RIGHT

    @property
    def _health_colour(self) -> pygame.Color:
        """Returns the colour used in the character's health bar given their quantity of health.

        Returns:
            A green hue for a healthy character, red for an severely wounded character, or a colour
            in between.
        """
        if self.health.hp < settings.MAX_HEALTH // 2:
            return pygame.Color(255, int(255 * self.health.hp * 2 / settings.MAX_HEALTH), 0)

        else:
            return pygame.Color(
                int(255 * (settings.MAX_HEALTH - self.health.hp) * 2 / settings.MAX_HEALTH),
                255,
                0,
            )

    def _draw_controller_triangle(
        self, display: bombsite.display.Display, colour: pygame.Color
    ) -> None:
        """Draws a triangle showing control over a character.

        Args:
            display: The display onto which the triangle is being drawn.
            colour: The colour of the triangle.
        """
        pygame.draw.polygon(
            display.screen,
            colour,
            [
                self.kinematics.pos + np.array((0, -20)) - display.pos,
                self.kinematics.pos + np.array((-5, -30)) - display.pos,
                self.kinematics.pos + np.array((5, -30) - display.pos),
            ],
        )

    def _draw_aim(self, display: bombsite.display.Display) -> None:
        """Draws the aim of the character onto the playing field.

        Args:
            display: The display onto which the character is to be drawn.
        """
        # Draws the aim of the controlled character.
        if not self.control.preparing_attack and self.pf.game_state.controlled_can_attack:
            pygame.draw.line(
                display.screen,
                pygame.Color("darkgreen"),
                self.kinematics.pos - display.pos,
                self.kinematics.pos + 50 * self.angle_array() - display.pos,
            )

        # Draws the aim of the controlled character.
        elif self.control.preparing_attack:
            pygame.draw.line(
                display.screen,
                pygame.Color("black"),
                self.kinematics.pos - display.pos,
                self.kinematics.pos
                + 12 * self.control.firing_strength * self.angle_array()
                - display.pos,
            )

    def _draw_health(self, display: bombsite.display.Display) -> None:
        """Draws the character's health bar onto the playing field.

        Args:
            display: The display onto which the health bar is to be drawn.
        """
        pygame.draw.rect(
            display.screen,
            self._health_colour,
            (
                (self.kinematics.x - 20 - display.x, self.kinematics.y - 20 - display.y),
                (int(40 * self.health.hp / 100), 10),
            ),
        )
        pygame.draw.rect(
            display.screen,
            pygame.Color("black"),
            ((self.kinematics.x - 20 - display.x, self.kinematics.y - 20 - display.y), (40, 10)),
            1,
        )

    def _display_name(
        self, display: bombsite.display.Display, draw_pos: npt.NDArray[np.int_]
    ) -> None:
        """Writes the character's name onto the playing field.

        Args:
            display: The display onto which the character's name is to be drawn.
            draw_pos: The position of the character relative to the screen.
        """
        text_surface = self.font.render(self.details.name, 1, self.details.team.colour)
        draw_x, draw_y = draw_pos
        display.screen.blit(text_surface, (draw_x - text_surface.get_width() // 2, draw_y - 50))

    def draw(self, display: bombsite.display.Display) -> None:
        """Draws the character onto the playing field.

        Args:
            display: The display onto which the character is to be drawn.
        """
        if not self.health.alive:
            return

        draw_pos = self.kinematics.pos.astype(int) - display.pos

        if self.control.controlled:
            # Draws a triangle above the controlled character.
            self._draw_controller_triangle(display, self.details.team.colour)

            # Draws the aim of the controlled character.
            self._draw_aim(display)

        # Draws the health bar of the character.
        self._draw_health(display)
        self._display_name(display, draw_pos)

        pygame.draw.circle(display.screen, self.details.team.colour, draw_pos, 6)

    def _update_walk(self) -> None:
        """Changes the position of the character if walking."""
        if self.control.walking == Walking.LEFT:
            if self._surrounding_is(
                np.array(
                    (
                        (0, 0, -1),
                        (0, 0, -1),
                        (1, 1, -1),
                    )
                )
            ):
                self.kinematics.x -= 1
            elif self._surrounding_is(np.array(((0, 0, -1), (1, 0, -1), (-1, 1, -1)))):
                self.kinematics.x -= 1
                self.kinematics.y -= 1
            elif self._surrounding_is(np.array(((0, 0, -1), (0, 0, -1), (0, 1, -1)))):
                self.kinematics.x -= 1
                self.kinematics.y += 1

        elif self.control.walking == Walking.RIGHT:
            if self._surrounding_is(
                np.array(
                    (
                        (-1, 0, 0),
                        (-1, 0, 0),
                        (-1, 1, 1),
                    )
                )
            ):
                self.kinematics.x += 1
            elif self._surrounding_is(np.array(((-1, 0, 0), (-1, 0, 1), (-1, 1, -1)))):
                self.kinematics.x += 1
                self.kinematics.y -= 1
            elif self._surrounding_is(np.array(((-1, 0, 0), (-1, 0, 0), (-1, 1, 0)))):
                self.kinematics.x += 1
                self.kinematics.y += 1

    def _update_facing_direction(self) -> None:
        """Updates the direction in which the character is facing."""
        if self._moving_left:
            self.facing_l = True

        elif self._moving_right:
            self.facing_r = True

    def update(self) -> None:
        """Updates the character's attributes.

        Raises:
            ValueError: If after 100 iterations of collision detection a new position has not been
                found, the game crashes.
        """
        # Doesn't update the position.
        if not self.health.alive:
            return

        # Operates the AI if needed.
        if self.control.controlled and self.details.team.ai is not None:
            self.details.team.ai.run_ai(self)

        # If the character is able to stand and is walking, updates the
        # walk.
        if self._is_standing:
            if self.control.walking != Walking.NA:
                self._update_walk()

            self._update_facing_direction()

            return

        # Makes the character accelerate downwards.
        self.apply_gravity()

        first_bound = self.kinematics.pos.astype(int)
        last_bound = (self.kinematics.pos + self.kinematics.vel).astype(int)

        if self.pf.collision_pixel(*last_bound):
            if not self.pf.collision_pixel(*first_bound):
                for _i in range(100):
                    middle_bound = np.ceil((first_bound + last_bound) / 2).astype(int)

                    if np.array_equal(middle_bound, last_bound) or np.array_equal(
                        middle_bound, first_bound
                    ):
                        self.set_pos(first_bound)
                        break

                    if self.pf.collision_pixel(*middle_bound):
                        last_bound = middle_bound
                    else:
                        first_bound = middle_bound

                else:
                    raise ValueError("Cannot resolve position.")

            self._bounce()

        else:
            self.set_pos(self.kinematics.pos + self.kinematics.vel)

        self._update_facing_direction()
        self._check_outside_boundaries()

    def visible(self) -> bool:
        """Determines whether or not the character is visible.

        Returns:
            Character visibility depending on if the character is alive.
        """
        return self.health.alive

    def take_control(self) -> Self:
        """Gives control of the character to the user.

        Returns:
            The character itself.
        """
        self.control.controlled = True
        self.pf.last_controlled = self
        return self

    def relinquish_control(self) -> None:
        """Takes away control of the character from the user."""
        self.control.walking = Walking.NA
        self.control.controlled = False
        self.control.preparing_attack = False

    def _jump(self) -> None:
        """Causes the character to leap."""
        if self._is_standing:
            self.set_vy(self.kinematics.vy - 2.5)
            if self.control.walking == Walking.LEFT:
                self.set_vx(-1.0)
            elif self.control.walking == Walking.RIGHT:
                self.set_vx(1.0)

    def _walk_left(self) -> None:
        """Makes the character attempt to walk to the left."""
        if (
            self._is_standing
            and self.pf.game_state.controlled_can_attack
            or self.pf.game_state.controlled_can_just_walk
        ):
            if not self.pf.collision_pixel(self.kinematics.x - 1, self.kinematics.y - 2):
                self.control.walking = Walking.LEFT

    def _walk_right(self) -> None:
        """Makes the character attempt to walk to the right."""
        if (
            self._is_standing
            and self.pf.game_state.controlled_can_attack
            or self.pf.game_state.controlled_can_just_walk
        ):
            if not self.pf.collision_pixel(self.kinematics.x + 1, self.kinematics.y - 2):
                self.control.walking = Walking.RIGHT

    def _stop_walking(self) -> None:
        """Makes the character stop attempting to walk."""
        self.control.walking = Walking.NA
        if self._is_standing:
            self.set_vx(0.0)

    def start_attack(self) -> None:
        """Makes the character begin an attack if possible."""
        if self._is_standing:
            self._stop_walking()
            self.control.preparing_attack = True

    def prepare_attack(self, target_firing_strength: Optional[float] = None) -> None:
        """Increases the duration over which the character's attack is
        occurring and releases the attack if it has gone on too long.

        Args:
            target_firing_strength: The targeted firing strength if controlled by an AI, otherwise
                None.
        """
        if self.control.preparing_attack and self.pf.game_state.controlled_can_attack:
            self.control.firing_strength += 0.12

            if (
                target_firing_strength is not None
                and self.control.firing_strength > target_firing_strength
            ):
                self.control.firing_strength = target_firing_strength

            elif self.control.firing_strength > settings.MAXIMUM_FIRING_POWER:
                self.control.firing_strength = settings.MAXIMUM_FIRING_POWER
                self.release_attack()

            return

    def release_attack(self) -> None:
        """Deploys a projectile from the character's position."""
        if self.control.preparing_attack and self.pf.game_state.controlled_can_attack:
            self.control.preparing_attack = False

            projectile_vel = self.angle_array() * self.control.firing_strength
            self.control.firing_strength = 0

            self.pf.world_objects.append(
                Rocket(
                    self.pf,
                    (self.kinematics.x, self.kinematics.y),
                    (float(projectile_vel[0]), float(projectile_vel[1])),
                    self,
                )
            )

            self.pf.game_state.controlled_can_attack = False
            self.pf.game_state.controlled_can_just_walk = True
            self.pf.refresh_tick()

    def aim_upwards(self, cap: float = settings.MAXIMUM_FIRING_ANGLE) -> None:
        """Raises the angle at which the character is firing.

        Args:
            cap: The maximum firing angle possible.
        """
        self.control.firing_angle = min((cap, self.control.firing_angle + 0.5))

    def aim_downwards(self, cap: float = settings.MINIMUM_FIRING_ANGLE) -> None:
        """Lowers the angle at which the character is firing.

        Args:
            cap: The lowest firing angle possible.
        """
        self.control.firing_angle = max((cap, self.control.firing_angle - 0.5))

    def angle_array(
        self, angle: Optional[int] = None, facing_l: Optional[bool] = None
    ) -> npt.NDArray[np.double]:
        """Converts the firing angle into a unit vector in that direction.

        Args:
            angle: The angle at which the firing angle is being calculated. Uses the character's
                firing angle if none given.
            facing_l: The direction the character is facing. True if the character is facing left,
                otherwise False.

        Returns:
            An array with the horizontal and vertical components of the firing direction.
        """
        angle_radians = np.radians(angle if angle else self.control.firing_angle)
        facing_l = facing_l if facing_l is not None else self.facing_l
        return np.array((np.cos(angle_radians) * (-1) ** facing_l, -np.sin(angle_radians)))

    def process_key_presses(self, pressed_keys: pygame.key.ScancodeWrapper) -> None:
        """Reacts to the users commands from held keys.

        Args:
            pressed_keys: A mapping from the keys to whether or not they are pressed.
        """
        if pressed_keys[pygame.K_LEFT]:
            self._walk_left()

        elif pressed_keys[pygame.K_RIGHT]:
            self._walk_right()

        else:
            self._stop_walking()

        if pressed_keys[pygame.K_SPACE]:
            self._jump()

        if pressed_keys[pygame.K_RETURN]:
            self.prepare_attack()

        else:
            self.release_attack()

        if pressed_keys[pygame.K_UP]:
            self.aim_upwards()

        elif pressed_keys[pygame.K_DOWN]:
            self.aim_downwards()

    def _check_outside_boundaries(self) -> None:
        """Checks if the character has fallen outside the map boundaries."""
        if not self.health.alive:
            return

        field_width, field_height = self.pf.mask.shape

        if (
            self.kinematics.x < 0
            or self.kinematics.x > field_width
            or self.kinematics.y > field_height
        ):
            logger.logger.log(f"{self} has fallen off the face of the earth!")
            self.health.alive = False
            self.null_velocity()

    def _surrounding_is(self, match: npt.NDArray[np.int_]) -> bool:
        """Checks if the mask around the character matches the template given.

        Args:
            match: A 3x3 array, centered on the character's position,
                with the expected values:
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

        # Obtains the part of the mask around the character, using
        # clipping to prevent index errors when the character is outside
        # the map boundaries.
        x, y = self.kinematics.pos.astype(int)
        cols = self.pf.mask.take(range(x - 1, x + 2), axis=0, mode="clip")
        section = cols.take(range(y - 1, y + 2), axis=1, mode="clip").transpose()

        # An error only occurs where the sum of the mask and match at a
        # position is equal to 1, which only happens when one value is
        # 0 and another value is 1, meaning that whatever value checked
        # in the match is not in the mask.
        return 1 not in (match + section)

    def _bounce(self) -> None:
        """Bounces off whatever surface the character hit."""
        # Calculates the speed at which the character hits the ground.
        entry_speed = np.linalg.norm(self.kinematics.vel)

        # If the collision is a small one, the character stops and does
        # not bounce.
        if entry_speed < 5:
            self.null_velocity()
            return

        # Damages the character in proportion to how damaged it was.
        self.health.hp -= int(4 * entry_speed)

        # Checks if the collision of the character was fatal.
        if self.health.hp <= 0:
            # Destroys the character.
            self.health.alive = False
            self.null_velocity()

            # Sends a message depending on who killed the
            # character.
            logger.logger.log(f"{self} fought the ground and the ground won!")

        # Bounces if the ground is flat.
        if self._surrounding_is(np.array(((0, 0, 0), (0, 0, 0), (1, 1, 1)))):
            self.set_vx(self.kinematics.vx * 0.8)
            self.set_vy(self.kinematics.vy * -0.4)

        # Bounces if the ground is sloped downwards to the right.
        elif self._surrounding_is(np.array(((0, 0, 0), (1, 0, 0), (-1, 1, -1)))):
            self.set_vx(self.kinematics.vy * 0.6)
            self.set_vy(self.kinematics.vx * 0.6)

        # Bounces if the ground is sloped downwards to the left.
        elif self._surrounding_is(np.array(((0, 0, 0), (0, 0, 1), (-1, 1, -1)))):
            self.set_vx(self.kinematics.vy * -0.6)
            self.set_vy(self.kinematics.vx * -0.6)

        # If the ground is too unpredictable, the character stops
        # falling.
        else:
            self.null_velocity()
