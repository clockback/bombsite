from dataclasses import dataclass


@dataclass
class GameState:
    """The particular game state active for the playing field."""

    controlled_can_attack: bool = True
    controlled_can_just_walk: bool = False
    waiting_for_things_to_settle: bool = True
    between_turns: bool = False
    end_game: bool = False

    # Keeps a record of when the game state was last changed.
    last_general_tick: int = 0
