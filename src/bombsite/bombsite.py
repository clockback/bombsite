#!/usr/bin/env python

"""bombsite.py is the entry point for the Bombsite game.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import Literal

import pygame

import bombsite.display
from bombsite import settings, ticks
from bombsite.world import playing_field
from bombsite.world.teams import Team

pygame.init()

display: bombsite.display.Display = bombsite.display.Display()
pf: playing_field.PlayingField = playing_field.PlayingField("hills")


def test_bombsite() -> None:
    """Ensures that the playing field has teams/characters."""
    # Creates the three teams.
    team_1 = Team(pf)
    team_2 = Team(pf, has_ai=True)
    team_3 = Team(pf, has_ai=True)

    # Creates the list of teams.
    pf.teams.extend([team_1, team_2, team_3])

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

    pf.world_objects = characters
    next(pf.next_team().character_queue).take_control()


def mainloop() -> bool:
    """Handles a single instance of the mainloop.

    Returns:
        Whether or not the program needs to abort.
    """
    # Iterates over every pygame event.
    for event in pygame.event.get():
        # The game quits if given a quit command.
        if event.type == pygame.QUIT:
            return True

        # The game quits if the event was the user pressing the escape
        # key.
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            character = pf.controlled_character
            if character.details.team.ai is None:
                character.start_attack()

    # Finds all the keys that are pressed and processes them.
    pf.process_key_presses(pygame.key.get_pressed())

    focus = pf.update()

    display.update(pf, focus)

    ticks.clock.tick(settings.TICKS_PER_SECOND)

    return False


def main() -> Literal[0]:
    """Runs the game's mainloop.

    Returns:
        A return code of zero to indicate success.
    """
    test_bombsite()
    display.set_focus(*pf.controlled_character.kinematics.pos.astype(int))

    game_exit = False
    while not game_exit:
        game_exit = mainloop()
        ticks.total_ticks += 1

    return 0


if __name__ == "__main__":
    main()
