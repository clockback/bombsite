"""playing_field.py keeps track of all things within a single match.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Generator, Optional

import numpy as np
import numpy.typing as npt
import pygame

import bombsite.display
from bombsite import logger, settings, ticks
from bombsite.world import gamestate, teams, world_objects


class PlayingField:
    """The area where the characters run.

    Attributes:
        image: The base image of the solid ground for the playing field.
        mask: An array the size of the playing field which indicates whether or not there is solid
            ground at a corresponding coordinate.
        teams: A list of teams that are fighting one another on the playing field.
        last_controlled: Whichever character is either being controlled presently or was most
            recently controlled on the playing field.
        world_objects: A list of all physical world objects on the playing field, such as characters
            and projectiles.
        game_state: A data structure from which the present game state can be inferred, such as
            whether or not a character may or may not move.
        display: The display onto which the playing field is being rendered.
    """

    def __init__(self, name: str, display: bombsite.display.Display) -> None:
        """Creates the playing field.

        Args:
            name: The name of the playing field which corresponds with its image.
            display: The display which shows the playing field.
        """
        # Obtains and loads the image for the playing field.
        path_to_image = Path(__file__).parent.parent / "images" / "playing_fields" / f"{name}.png"
        self.image: pygame.Surface = pygame.image.load(path_to_image).convert_alpha()

        # Finds the playing field's image's alpha array.
        self.mask: npt.NDArray[np.uint8] = pygame.surfarray.array_alpha(self.image)

        # Applies an initial mask on the image to remove
        # semi-transparent pixels.
        self.process_mask(lambda _x, _y, mask: mask == 255)

        # Creates the two teams.
        team_1 = teams.Team(self)
        team_2 = teams.Team(self, has_ai=True)
        team_3 = teams.Team(self, has_ai=True)

        # Creates the list of teams.
        self.teams: list[teams.Team] = [team_1, team_2]

        # Creates a list of characters.
        characters = [
            team_1.add_character(100, 500, "Joey"),
            team_2.add_character(200, 500, "Ronald"),
            team_3.add_character(300, 500, "Ricky"),
            team_1.add_character(400, 500, "John"),
            team_2.add_character(500, 500, "Tamara"),
            team_3.add_character(600, 500, "Anne"),
            team_1.add_character(700, 500, "Samantha"),
            team_2.add_character(800, 500, "Felicity"),
            team_3.add_character(900, 500, "Alex"),
        ]

        # Gives control of the first-created character to the user.
        current_team = teams.Team.next_team()
        self.last_controlled: world_objects.Character = next(
            current_team.character_queue
        ).take_control()

        # Creates the world objects.
        self.world_objects: list[world_objects.WorldObject] = characters.copy()

        # Sets variables that determine the state of the game.
        self.game_state: gamestate.GameState = gamestate.GameState()

        # Stores the display.
        self.display: bombsite.display.Display = display
        self.display.set_focus(*self.controlled_character.pos.astype(int))

    def get_centre(self) -> Optional[npt.NDArray[np.int_]]:
        """Finds the centre point of all moving objects on screen.

        Returns:
            The new position for the focus if there are moving objects.
        """
        xs = []
        ys = []

        for wo in self.world_objects:
            if np.any(wo.vel):
                xs.append(wo.x)
                ys.append(wo.y)

        if xs:
            return np.array((np.average(xs), np.average(ys)))

        return None

    def update(self) -> bool:
        """Updates the state of all objects in the playing field.

        Returns:
            Whether or not the program should abort.
        """
        self.process_tick()

        for wo in self.world_objects:
            wo.update()

        # Pans to the centre of the projectile.
        display_focus = self.get_centre()
        if display_focus is not None:
            self.display.set_focus(*display_focus)

        return False

    def process_tick(self) -> None:
        """Assesses if the game state should change."""
        # Calculates the time in seconds since the game state changed.
        no_ticks = ticks.total_ticks - self.game_state.last_general_tick
        time = no_ticks / settings.TICKS_PER_SECOND

        # Ends the time to attack if the user was too slow.
        if self.game_state.controlled_can_attack:
            if time > settings.TIME_TO_ACT:
                self.controlled_character.relinquish_control()
                self.refresh_tick()
                self.game_state.controlled_can_attack = False
                self.game_state.between_turns = True

        # Ends the time to walk after their attack if enough time has
        # passed.
        elif self.game_state.controlled_can_just_walk:
            if time > settings.TIME_TO_RETREAT:
                if self.controlled_character:
                    self.controlled_character.relinquish_control()
                self.refresh_tick()
                self.game_state.controlled_can_just_walk = False
                self.game_state.waiting_for_things_to_settle = True

        elif self.game_state.waiting_for_things_to_settle:
            if self.settled:
                self.game_state.waiting_for_things_to_settle = False
                self.game_state.between_turns = True
                self.refresh_tick()

        # Switches to a new time if enough time has passed.
        elif self.game_state.between_turns:
            if time > settings.TIME_TO_WAIT_FOR_TURN:
                if len(teams.Team.get_alive_teams()) > 1:
                    next_team = teams.Team.next_team(self.last_controlled.team)
                    self.last_controlled = next(next_team.character_queue)
                    self.last_controlled.take_control()
                    self.game_state.between_turns = False
                    self.game_state.controlled_can_attack = True
                    self.display.set_focus(*self.controlled_character.pos.astype(int))
                    self.refresh_tick()

                else:
                    self.game_state.between_turns = False
                    self.game_state.end_game = True
                    self.announce_victor()

    def announce_victor(self) -> None:
        """Creates a log message indicating the outcome of the match."""
        for team in self.teams:
            if team.check_if_alive():
                logger.logger.log(f"{team} is victorious!")
                break
        else:
            logger.logger.log("Oh the humanity!")

    @property
    def settled(self) -> bool:
        """Determines whether or not things are actively happening on the field.

        Returns:
            Boolean for whether or not anything is happening, such as a character or projectile
            moving.
        """
        for wo in self.world_objects:
            if np.any(wo.vel):
                return False

        return True

    def refresh_tick(self) -> None:
        """Acknowledges when the last change in state occurred."""
        self.game_state.last_general_tick = ticks.total_ticks

    def process_mask(
        self,
        overlay: Callable[
            [npt.NDArray[np.int64], npt.NDArray[np.int64], npt.NDArray[np.uint8]], None
        ],
    ) -> None:
        """Takes a playing field mask and applies it to the existing mask.

        Args:
            overlay: A function which takes the x index, the y index, and the existing mask values
                to create a new mask.
        """
        # Obtains the size of the image.
        width = self.image.get_width()
        height = self.image.get_height()

        # Creates two index matrices.
        x = np.column_stack([np.arange(width)] * height)
        y = np.row_stack([np.arange(height)] * width)

        # Applies the mask.
        self.mask = self.mask & overlay(x, y, self.mask)

        # Obtains the mutable array for the present alpha of the image
        # and overwrites the old alpha channel.
        surface_alpha = np.array(self.image.get_view("A"), copy=False)
        surface_alpha[:, :] = self.mask * 255

    @property
    def characters(self) -> Generator[world_objects.Character, None, None]:
        """Yields each world object that is a character.

        Yields:
            Each character in the world.
        """
        for world_object in self.world_objects:
            if isinstance(world_object, world_objects.Character):
                yield world_object

    @property
    def projectiles(self) -> Generator[world_objects.Projectile, None, None]:
        """Yields each world object that is a projectile.

        Yields:
            Each projectile in the world.
        """
        for world_object in self.world_objects:
            if isinstance(world_object, world_objects.Projectile):
                yield world_object

    @property
    def controlled_character(self) -> Optional[world_objects.Character]:
        """Returns whichever character is being controlled by the user.

        Returns:
            The currently selected character or None if no character is selected.
        """
        # Iterates over all objects in the world which are the user.
        for character in self.characters:
            if character.controlled:
                return character

        return None

    @controlled_character.setter
    def controlled_character(self, select_character: world_objects.Character) -> None:
        """Sets whichever character should be controlled, deselecting
        other characters.

        Args:
            select_character: The character who should now be controlled.
        """
        for character in self.characters:
            if character.controlled is select_character:
                character.take_control()
            else:
                character.relinquish_control()

    def process_key_presses(self, pressed_keys: pygame.key.ScancodeWrapper) -> None:
        """Handles all keys that are currently pressed.

        Args:
            pressed_keys: The mapping with key bindings to whether or not they are being pressed.
        """
        character = self.controlled_character
        if character and character.team.ai is None:
            character.process_key_presses(pressed_keys)

    def collision_pixel(self, x: float, y: float) -> bool:
        """Determines if a pixel location on the playing field is solid or not.

        Args:
            x: The x-location of the pixel.
            y: The y-location of the pixel.

        Returns:
            Whether or not the pixel location is a solid.
        """
        return (
            0 <= x < self.mask.shape[0]
            and 0 <= y < self.mask.shape[1]
            and bool(self.mask[int(x), int(y)])
        )

    def explosion(
        self,
        pos: npt.NDArray[np.double],
        caused_by: world_objects.Character,
        radius: int = 40,
    ) -> None:
        """Causes an explosion to damage the nearby terrain and characters.

        Args:
            pos: The source location of the explosion.
            caused_by: The character who initiated the explosion.
            radius: The radius of the blast.
        """
        # Damages the terrain in a circular shape.
        self.process_mask(lambda x, y, _mask: (x - pos[0]) ** 2 + (y - pos[1]) ** 2 > radius**2)

        # Affects nearby characters caught in the blast.
        for character in self.characters:
            # Ignores dead characters.
            if not character.alive:
                continue

            # Finds the distance from the blast of the character.
            vector = character.pos - pos
            distance = np.linalg.norm(vector)

            # Only affects the character if sufficiently close.
            if distance < radius:
                # Creates a direction in which the character is flung,
                # complete with upwards momentum.
                blast_vector = vector + np.array((0, -25))
                blast_direction = blast_vector / np.linalg.norm(blast_vector)

                # Damages the character depending on how close the
                # explosion was.
                character.health -= radius - distance

                # Kills the character if it runs out of health.
                if character.health <= 0:
                    character.alive = False
                    character.vel = np.array((0.0, 0.0))

                    # Sends a message depending on who killed the
                    # character.
                    if caused_by is character:
                        logger.logger.log(f"{caused_by} has committed seppuku!")
                    elif caused_by.team == character.team:
                        logger.logger.log(f"{caused_by} accidentally killed {character}!")
                    else:
                        logger.logger.log(f"{caused_by} killed {character}!")

                # Flings the character in the appropriate direction.
                else:
                    character.vel += (blast_direction * (radius - distance)) * 0.1

    def time_left_on_clock(self) -> float:
        """Determines how much time is left on the clock to perform an action.

        Returns:
            The number of seconds until the game state changes.
        """
        ticks_passed = ticks.total_ticks - self.game_state.last_general_tick
        time_passed = ticks_passed / settings.TICKS_PER_SECOND
        return np.ceil(settings.TIME_TO_ACT - time_passed)
