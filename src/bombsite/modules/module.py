"""module.py allows Bombsite to behave according to whichever module is active.

Copyright © 2024 - Elliot Simpson
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod

import pygame

from bombsite.modules.modulecomponents import ModuleComponent


class Module(metaclass=ABCMeta):
    """Base class from which modules all inherit."""

    @abstractmethod
    def __init__(self, module_component: ModuleComponent) -> None:
        """Initializes the module.

        Args:
            module_component: The semi-custom data to be passed to the module.
        """

    @abstractmethod
    def process_event(self, event: pygame.event.Event) -> ModuleComponent | None | SystemExit:
        """Handles an incoming event.

        Args:
            event: The most recently polled user event.

        Returns:
            Either None, a tuple containing a new module component to be used, or a game exit.
        """

    @abstractmethod
    def update(self) -> ModuleComponent | None | SystemExit:
        """Updates the module over the course of a tick.

        Returns:
            Either None, a tuple containing a new module to be used, or a game exit.
        """

    @abstractmethod
    def render(self) -> None:
        """Displays the module's contents onto the screen."""
