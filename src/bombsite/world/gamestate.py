"""gamestate.py provides data objects that indicate the activity that is permitted within the game.

Copyright © 2024 - Elliot Simpson
"""

from dataclasses import dataclass


@dataclass
class GameState:
    """The particular game state active for the playing field.

    Attributes:
        * controlled_can_attack: If set to True, whichever character is presently being controlled
            is able to walk and perform attacks.
        * controlled_can_just_walk: If set to True, whichever character is presently being
            controlled is able to walk, but unable to perform attacks.
        * waiting_for_things_to_settle: If set to True, there are no characters being controlled,
            but the physics of the world is not yet stable.
        * between_turns: If set to True, the game is waiting for a short period before either giving
            control to the next character or ending the game.
        * end_game: If set to True, there is no gameplay left and no further control to characters
            given.
        * last_general_tick: An integer value which indicates at which tick did a certain game state
            change.
    """

    controlled_can_attack: bool = True
    controlled_can_just_walk: bool = False
    waiting_for_things_to_settle: bool = True
    between_turns: bool = False
    end_game: bool = False
    last_general_tick: int = 0
