#!/usr/bin/env python

"""bombsite.py is the entry point for the Bombsite game.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from typing import Literal

import pygame

import bombsite.modules.mainmenumodule
import bombsite.modules.module
import bombsite.modules.modulecomponents
from bombsite import settings, ticks
from bombsite.modules.moduleenum import ModuleEnum
from bombsite.modules.moduleindex import get_module_type

pygame.init()


def get_screen() -> pygame.Surface:
    """Creates a window for the game.

    Returns:
        The window.
    """
    # Creates the window.
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

    # Sets a name for the window.
    pygame.display.set_caption("Bombsite")

    return screen


def mainloop(
    module: bombsite.modules.module.Module,
) -> bombsite.modules.module.ModuleComponent | None | SystemExit:
    """Runs a single tick in the game.

    Args:
        module: The current Bombsite module.

    Returns:
        The module component to be loaded in the next tick, or a SystemExit if the game should
        abort.
    """
    for event in pygame.event.get():
        result = module.process_event(event)
        if result is not None:
            return result

    result = module.update()
    module.render()

    ticks.clock.tick(settings.TICKS_PER_SECOND)
    ticks.total_ticks += 1

    return result


def load_module(
    module_component: bombsite.modules.modulecomponents.ModuleComponent, /
) -> bombsite.modules.module.Module:
    """Loads a module.

    Args:
        module_component: The blueprint for the future module.

    Returns:
        The newly loaded module.
    """
    return get_module_type[module_component.module_reference](module_component)


def main() -> Literal[0]:
    """Runs the game's mainloop.

    Returns:
        A return code of zero to indicate success.
    """
    module = load_module(bombsite.modules.modulecomponents.ModuleComponent(ModuleEnum.MAIN_MENU))
    module_component: bombsite.modules.modulecomponents.ModuleComponent | None | SystemExit = None

    while not isinstance(module_component, SystemExit):
        if isinstance(module_component, bombsite.modules.module.ModuleComponent):
            module = load_module(module_component)

        module_component = mainloop(module)

    return 0


if __name__ == "__main__":
    main()
