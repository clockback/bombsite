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

pygame.init()

display: bombsite.display.Display = bombsite.display.Display()
pf: playing_field.PlayingField = playing_field.PlayingField("hills", display)


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
            if character and pf.controlled_character.team.ai is None:
                character.start_attack()

    # Finds all the keys that are pressed and processes them.
    pf.process_key_presses(pygame.key.get_pressed())

    pf.update()

    display.update(pf)

    ticks.clock.tick(settings.TICKS_PER_SECOND)

    return False


def main() -> Literal[0]:
    """Runs the game's mainloop.

    Returns:
        A return code of zero to indicate success.
    """
    game_exit = False
    while not game_exit:
        game_exit = mainloop()
        ticks.total_ticks += 1

    return 0


if __name__ == "__main__":
    main()
