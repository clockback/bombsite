"""world_objects.py is the module providing the objects that appear on the playing field.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

import abc
import random
from pathlib import Path
from typing import Optional

import numpy as np
import numpy.typing as npt
import pygame.key
from typing_extensions import Self

import bombsite.display
from bombsite import logger, settings
from bombsite.world import playing_field, teams


class WorldObject(abc.ABC):
    """Any world object on the playing field."""

    def __init__(
        self,
        pf: playing_field.PlayingField,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = 0.0,
    ) -> None:
        """Creates the world object using the provided parameters.

        Args:
            pf: The playing field in which the object is placed.
            x: The x-position of the object.
            y: The y-position of the object.
            vx: The x-velocity of the object.
            vy: The y-velocity of the object.
        """
        self.pos: npt.NDArray[np.double] = np.array((x, y), dtype=np.double)
        self.vel: npt.NDArray[np.double] = np.array((vx, vy), dtype=np.double)
        self.pf: playing_field.PlayingField = pf

    def debug_show_position(self, r: int = 3) -> None:
        """Displays the map area surrounding the character.

        Args:
            r: The radius around the character to be displayed.
        """
        x_slice = slice(int(self.x) - r + 1, int(self.x) + r)
        y_slice = slice(int(self.y) - r + 1, int(self.y) + r)
        section = self.pf.mask[x_slice, y_slice]
        for row in section.transpose():
            print("".join("X" if mask_value else "." for mask_value in row))

    @property
    def x(self) -> float:
        """The getter for the x-component of the object's position.

        Returns:
            The world object's floating-point-value x-position.
        """
        return float(self.pos[0])

    @property
    def y(self) -> float:
        """The getter for the y-component of the object's position.

        Returns:
            The world object's floating-point-value y-position.
        """
        return float(self.pos[1])

    @x.setter
    def x(self, value: float) -> None:
        """The setter for the x-component of the object's position.

        Args:
            value: The new world object's x-position.
        """
        self.pos[0] = value

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

    @property
    def vy(self) -> float:
        """The getter for the y-component of the object's velocity.

        Returns:
            The world object's floating-point-value y-velocity.
        """
        return float(self.vel[1])

    @vx.setter
    def vx(self, value: float) -> None:
        """The setter for the x-component of the object's velocity.

        Args:
            value: The new world object's x-velocity.
        """
        self.vel[0] = value

    @vy.setter
    def vy(self, value: float) -> None:
        """The setter for the y-component of the object's velocity.

        Args:
            value: The new world object's y-velocity.
        """
        self.vel[1] = value

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
        self.vy += 0.05


class Character(WorldObject):
    """A character that can move and attack."""

    font: pygame.font.Font = pygame.font.Font(
        Path(__file__).parent.parent / "fonts" / "playpen_sans" / "PlaypenSans-Regular.ttf",
        10,
    )
    """The font used to render the names of the characters."""

    def __init__(
        self,
        pf: playing_field.PlayingField,
        x: int,
        y: int,
        name: str,
        team: teams.Team,
    ) -> None:
        """Creates the character using the provided parameters.

        Args:
            pf: The playing field in which the character exists.
            x: The x-position of the character.
            y: The y-position of the character.
            name: The name of the character.
            team: The number team (starting from 1) in which the character is placed.
        """
        super().__init__(pf, x, y, 0, 0)
        self.name: str = name
        self.controlled: bool = False
        self.walking_l: bool = False
        self.walking_r: bool = False
        self.team: teams.Team = team
        self.preparing_attack: bool = False
        self.facing_l: bool = random.choice((True, False))
        self.facing_r: bool = not self.facing_l
        self.firing_angle: int = 30
        self.fire_strength: float = 0.0
        self.health: int = 100
        self.alive: bool = True

    def __str__(self) -> str:
        return self.name

    def is_alive(self) -> bool:
        """Returns whether or not the character is alive.

        Returns:
            If the character is alive, return True, otherwise False.
        """
        return self.alive

    @property
    def is_standing(self) -> bool:
        """Whether or not the character is standing on ground.

        Returns:
            Boolean for whether or not the character is standing on ground.
        """
        if self.vy == 0.0:
            if self.pf.collision_pixel(self.x, self.y + 1):
                if not self.pf.collision_pixel(self.x, self.y):
                    return True

        return False

    @property
    def moving_left(self) -> bool:
        """Whether or not the character is moving left.

        Returns:
            True if the character is either moving to the left, or is being commanded to walk to the
            left.
        """
        return self.vx < 0 or self.walking_l

    @property
    def moving_right(self) -> bool:
        """Whether or not the character is moving right.

        Returns:
            True if the character is either moving to the right, or is being commanded to walk to
            the right.
        """
        return self.vx > 0 or self.walking_r

    @property
    def health_colour(self) -> pygame.Color:
        """Returns the colour used in the character's health bar given their quantity of health.

        Returns:
            A green hue for a healthy character, red for an severely wounded character, or a colour
            in between.
        """
        if self.health < settings.MAX_HEALTH // 2:
            return pygame.Color(255, int(255 * self.health * 2 / settings.MAX_HEALTH), 0)

        else:
            return pygame.Color(
                int(255 * (settings.MAX_HEALTH - self.health) * 2 / settings.MAX_HEALTH),
                255,
                0,
            )

    def draw_controller_triangle(
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
                self.pos + np.array((0, -20)) - display.pos,
                self.pos + np.array((-5, -30)) - display.pos,
                self.pos + np.array((5, -30) - display.pos),
            ],
        )

    def draw_aim(self, display: bombsite.display.Display) -> None:
        """Draws the aim of the character onto the playing field.

        Args:
            display: The display onto which the character is to be drawn.
        """
        # Draws the aim of the controlled character.
        if not self.preparing_attack and self.pf.game_state.controlled_can_attack:
            pygame.draw.line(
                display.screen,
                pygame.Color("darkgreen"),
                self.pos - display.pos,
                self.pos + 50 * self.angle_array() - display.pos,
            )

        # Draws the aim of the controlled character.
        elif self.preparing_attack:
            pygame.draw.line(
                display.screen,
                pygame.Color("black"),
                self.pos - display.pos,
                self.pos + 12 * self.fire_strength * self.angle_array() - display.pos,
            )

    def draw_health(self, display: bombsite.display.Display) -> None:
        """Draws the character's health bar onto the playing field.

        Args:
            display: The display onto which the health bar is to be drawn.
        """
        pygame.draw.rect(
            display.screen,
            self.health_colour,
            (
                (self.x - 20 - display.x, self.y - 20 - display.y),
                (int(40 * self.health / 100), 10),
            ),
        )
        pygame.draw.rect(
            display.screen,
            pygame.Color("black"),
            ((self.x - 20 - display.x, self.y - 20 - display.y), (40, 10)),
            1,
        )

    def display_name(
        self, display: bombsite.display.Display, draw_pos: npt.NDArray[np.int_]
    ) -> None:
        """Writes the character's name onto the playing field.

        Args:
            display: The display onto which the character's name is to be drawn.
            draw_pos: The position of the character relative to the screen.
        """
        text_surface = self.font.render(self.name, 1, teams.colours[self.team.team_number - 1])
        draw_x, draw_y = draw_pos
        display.screen.blit(text_surface, (draw_x - text_surface.get_width() // 2, draw_y - 50))

    def draw(self, display: bombsite.display.Display) -> None:
        """Draws the character onto the playing field.

        Args:
            display: The display onto which the character is to be drawn.
        """
        if not self.alive:
            return

        colour = teams.colours[self.team.team_number - 1]
        draw_pos = self.pos.astype(int) - display.pos

        if self.controlled:
            # Draws a triangle above the controlled character.
            self.draw_controller_triangle(display, colour)

            # Draws the aim of the controlled character.
            self.draw_aim(display)

        # Draws the health bar of the character.
        self.draw_health(display)
        self.display_name(display, draw_pos)

        pygame.draw.circle(display.screen, colour, draw_pos, 6)

    def update_walk(self) -> None:
        """Changes the position of the character if walking."""
        if self.walking_l:
            if self.surrounding_is(
                np.array(
                    (
                        (0, 0, -1),
                        (0, 0, -1),
                        (1, 1, -1),
                    )
                )
            ):
                self.x -= 1
            elif self.surrounding_is(np.array(((0, 0, -1), (1, 0, -1), (-1, 1, -1)))):
                self.x -= 1
                self.y -= 1
            elif self.surrounding_is(np.array(((0, 0, -1), (0, 0, -1), (0, 1, -1)))):
                self.x -= 1
                self.y += 1

        elif self.walking_r:
            if self.surrounding_is(
                np.array(
                    (
                        (-1, 0, 0),
                        (-1, 0, 0),
                        (-1, 1, 1),
                    )
                )
            ):
                self.x += 1
            elif self.surrounding_is(np.array(((-1, 0, 0), (-1, 0, 1), (-1, 1, -1)))):
                self.x += 1
                self.y -= 1
            elif self.surrounding_is(np.array(((-1, 0, 0), (-1, 0, 0), (-1, 1, 0)))):
                self.x += 1
                self.y += 1

    def update_facing_direction(self) -> None:
        """Updates the direction in which the character is facing."""
        if self.moving_left:
            self.facing_l = True
            self.facing_r = False

        elif self.moving_right:
            self.facing_r = True
            self.facing_l = False

    def update(self) -> None:
        """Updates the character's attributes.

        Raises:
            ValueError: If after 100 iterations of collision detection a new position has not been
                found, the game crashes.
        """
        # Doesn't update the position.
        if not self.alive:
            return

        # Operates the AI if needed.
        if self.controlled and self.team.ai is not None:
            self.team.ai.run_ai(self)

        # If the character is able to stand and is walking, updates the
        # walk.
        if self.is_standing:
            if self.walking_l or self.walking_r:
                self.update_walk()

            self.update_facing_direction()

            return

        # Makes the character accelerate downwards.
        self.apply_gravity()

        first_bound = self.pos.astype(int)
        last_bound = (self.pos + self.vel).astype(int)

        if self.pf.collision_pixel(*last_bound):
            if not self.pf.collision_pixel(*first_bound):
                for i in range(100):
                    middle_bound = np.ceil((first_bound + last_bound) / 2).astype(int)

                    if np.array_equal(middle_bound, last_bound) or np.array_equal(
                        middle_bound, first_bound
                    ):
                        self.pos = first_bound.astype(float)
                        break

                    if self.pf.collision_pixel(*middle_bound):
                        last_bound = middle_bound
                    else:
                        first_bound = middle_bound

                else:
                    raise ValueError("Cannot resolve position.")

            self.bounce()

        else:
            self.pos += self.vel

        self.update_facing_direction()
        self.check_outside_boundaries()

    def visible(self) -> bool:
        """Determines whether or not the character is visible.

        Returns:
            Character visibility depending on if the character is alive.
        """
        return self.alive

    def take_control(self) -> Self:
        """Gives control of the character to the user.

        Returns:
            The character itself.
        """
        self.controlled = True
        return self

    def relinquish_control(self) -> None:
        """Takes away control of the character from the user."""
        self.walking_l = False
        self.walking_r = False
        self.controlled = False
        self.preparing_attack = False

    def jump(self) -> None:
        """Causes the character to leap."""
        if self.is_standing:
            self.vy -= 2.5
            if self.walking_l:
                self.vx = -1.0
            elif self.walking_r:
                self.vx = 1.0

    def walk_left(self) -> None:
        """Makes the character attempt to walk to the left."""
        if (
            self.is_standing
            and self.pf.game_state.controlled_can_attack
            or self.pf.game_state.controlled_can_just_walk
        ):
            if not self.pf.collision_pixel(self.x - 1, self.y - 2):
                self.walking_l = True
                self.walking_r = False

    def walk_right(self) -> None:
        """Makes the character attempt to walk to the right."""
        if (
            self.is_standing
            and self.pf.game_state.controlled_can_attack
            or self.pf.game_state.controlled_can_just_walk
        ):
            if not self.pf.collision_pixel(self.x + 1, self.y - 2):
                self.walking_r = True
                self.walking_l = False

    def stop_walking(self) -> None:
        """Makes the character stop attempting to walk."""
        self.walking_l = self.walking_r = False
        if self.is_standing:
            self.vx = 0.0

    def start_attack(self) -> None:
        """Makes the character begin an attack if possible."""
        if self.is_standing:
            self.stop_walking()
            self.preparing_attack = True

    def prepare_attack(self, target_firing_strength: Optional[float] = None) -> None:
        """Increases the duration over which the character's attack is
        occurring and releases the attack if it has gone on too long.

        Args:
            target_firing_strength: The targeted firing strength if controlled by an AI, otherwise
                None.
        """
        if self.preparing_attack and self.pf.game_state.controlled_can_attack:
            self.fire_strength += 0.12

            if target_firing_strength is not None and self.fire_strength > target_firing_strength:
                self.fire_strength = target_firing_strength

            elif self.fire_strength > settings.MAXIMUM_FIRING_POWER:
                self.fire_strength = settings.MAXIMUM_FIRING_POWER
                self.release_attack()

            return

    def release_attack(self) -> None:
        """Deploys a projectile from the character's position."""
        if self.preparing_attack and self.pf.game_state.controlled_can_attack:
            self.preparing_attack = False

            projectile_vel = self.angle_array() * self.fire_strength
            self.fire_strength = 0

            self.pf.world_objects.append(
                Projectile(
                    self.pf,
                    self.x,
                    self.y,
                    float(projectile_vel[0]),
                    float(projectile_vel[1]),
                    settings.PROJECTILE_BLAST_RADIUS,
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
        self.firing_angle = min((cap, self.firing_angle + 0.5))

    def aim_downwards(self, cap: float = settings.MINIMUM_FIRING_ANGLE) -> None:
        """Lowers the angle at which the character is firing.

        Args:
            cap: The lowest firing angle possible.
        """
        self.firing_angle = max((cap, self.firing_angle - 0.5))

    def angle_array(
        self, angle: Optional[int] = None, facing_l: Optional[bool] = None
    ) -> npt.NDArray[np.double]:
        """Converts the firing angle into a unit vector in that
        direction.

        Args:
            angle: The angle at which the firing angle is being calculated. Uses the character's
                firing angle if none given.
            facing_l: The direction the character is facing. True if the character is facing left,
                otherwise False.

        Returns:
            An array with the horizontal and vertical components of the firing direction.
        """
        angle_radians = np.radians(angle if angle else self.firing_angle)
        facing_l = facing_l if facing_l is not None else self.facing_l
        return np.array((np.cos(angle_radians) * (-1) ** facing_l, -np.sin(angle_radians)))

    def process_key_presses(self, pressed_keys: pygame.key.ScancodeWrapper) -> None:
        """Reacts to the users commands from held keys.

        Args:
            pressed_keys: A mapping from the keys to whether or not they are pressed.
        """
        if pressed_keys[pygame.K_LEFT]:
            self.walk_left()

        elif pressed_keys[pygame.K_RIGHT]:
            self.walk_right()

        else:
            self.stop_walking()

        if pressed_keys[pygame.K_SPACE]:
            self.jump()

        if pressed_keys[pygame.K_RETURN]:
            self.prepare_attack()

        else:
            self.release_attack()

        if pressed_keys[pygame.K_UP]:
            self.aim_upwards()

        elif pressed_keys[pygame.K_DOWN]:
            self.aim_downwards()

    def check_outside_boundaries(self) -> None:
        """Checks if the character has fallen outside the map boundaries."""
        if not self.alive:
            return

        field_width, field_height = self.pf.mask.shape

        if self.x < 0 or self.x > field_width or self.y > field_height:
            logger.logger.log(f"{self} has fallen off the face of the earth!")
            self.alive = False
            self.vel = np.array((0.0, 0.0))

    def surrounding_is(self, match: npt.NDArray[np.int_]) -> bool:
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
        x, y = self.pos.astype(int)
        cols = self.pf.mask.take(range(x - 1, x + 2), axis=0, mode="clip")
        section = cols.take(range(y - 1, y + 2), axis=1, mode="clip").transpose()

        # An error only occurs where the sum of the mask and match at a
        # position is equal to 1, which only happens when one value is
        # 0 and another value is 1, meaning that whatever value checked
        # in the match is not in the mask.
        return 1 not in (match + section)

    def bounce(self) -> None:
        """Bounces off whatever surface the character hit."""
        # Calculates the speed at which the character hits the ground.
        entry_speed = np.linalg.norm(self.vel)

        # If the collision is a small one, the character stops and does
        # not bounce.
        if entry_speed < 5:
            self.vx = 0.0
            self.vy = 0.0
            return

        # Damages the character in proportion to how damaged it was.
        self.health -= int(4 * entry_speed)

        # Checks if the collision of the character was fatal.
        if self.health <= 0:
            # Destroys the character.
            self.alive = False
            self.vel = np.array((0.0, 0.0))

            # Sends a message depending on who killed the
            # character.
            logger.logger.log(f"{self} fought the ground and the ground won!")

        # Bounces if the ground is flat.
        if self.surrounding_is(np.array(((0, 0, 0), (0, 0, 0), (1, 1, 1)))):
            self.vy *= -0.4
            self.vx *= 0.8

        # Bounces if the ground is sloped downwards to the right.
        elif self.surrounding_is(np.array(((0, 0, 0), (1, 0, 0), (-1, 1, -1)))):
            self.vx = self.vy * 0.6
            self.vy = self.vx * 0.6

        # Bounces if the ground is sloped downwards to the left.
        elif self.surrounding_is(np.array(((0, 0, 0), (0, 0, 1), (-1, 1, -1)))):
            self.vx = self.vy * -0.6
            self.vy = self.vx * -0.6

        # If the ground is too unpredictable, the character stops
        # falling.
        else:
            self.vx = 0.0
            self.vy = 0.0


class Projectile(WorldObject):
    """A projectile that can damage characters."""

    def __init__(
        self,
        pf: playing_field.PlayingField,
        x: float,
        y: float,
        vx: float,
        vy: float,
        explosion_radius: int,
        sent_by: Character,
    ) -> None:
        """Creates the projectile using the provided parameters.

        Args:
            pf: The playing field in which the object is placed.
            x: The x-position of the projectile.
            y: The y-position of the projectile.
            vx: The x-velocity of the projectile.
            vy: The y-velocity of the projectile.
            explosion_radius: The radius of the resulting explosion.
        """
        super().__init__(pf, x, y, vx, vy)
        self.explosion_radius: int = explosion_radius
        self.sent_by: Character = sent_by

    def update(self) -> None:
        """Change's the projectile's attributes."""
        # Destroys the projectile if it leaves the map.
        if self.x < 0 or self.x > self.pf.mask.shape[0] or self.y > self.pf.mask.shape[1]:
            self.destroy()
            return

        # Causes the projectile to fall.
        self.apply_gravity()
        self.pos += self.vel

        # Detonates the projectile if it collides with the terrain.
        if self.pf.collision_pixel(*self.pos):
            self.pf.explosion(self.pos, self.sent_by, self.explosion_radius)
            self.destroy()

    def visible(self) -> bool:
        """Determines whether or not the projectile is visible.

        Returns:
            Projectile visibility. This is always True.
        """
        return True

    def destroy(self) -> None:
        """Removes the projectile."""
        self.pf.world_objects.remove(self)

    def phantom(self, target: Character) -> tuple[int, int]:
        """Estimates the expected result of the projectile.

        Args:
            target: The character that the phantom projectile is attempting to reach.

        Returns: A tuple containing the expected damage from the attack, and the distance from the
            targeted character.
        """
        net_damage = 0

        while True:
            self.apply_gravity()
            self.pos += self.vel

            # Destroys the projectile if it leaves the map.
            if self.x < 0 or self.x > self.pf.mask.shape[0] or self.y > self.pf.mask.shape[1]:
                return net_damage, np.linalg.norm(self.pos - target.pos)

            if self.pf.collision_pixel(*self.pos):
                # Affects nearby characters caught in the blast.
                for character in filter(Character.is_alive, self.pf.characters):
                    # Finds the distance from the blast of the character.
                    vector = character.pos - self.pos
                    distance = np.linalg.norm(vector)

                    # Only affects the character if sufficiently close.
                    if distance < self.explosion_radius:
                        damage = int(self.explosion_radius - distance)
                        if character.team is self.sent_by.team:
                            net_damage -= min((damage, character.health))
                        else:
                            net_damage += min((damage, character.health))

                break

        return net_damage, np.linalg.norm(self.pos - target.pos)
