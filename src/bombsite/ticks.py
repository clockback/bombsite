"""ticks.py is a module with global variables for the present game state.

Copyright © 2024 - Elliot Simpson
"""

import pygame

from bombsite.utils import fonts_path

pygame.font.init()

total_ticks: int = 0

font: pygame.font.Font = pygame.font.Font(
    fonts_path / "playpen_sans" / "PlaypenSans-Regular.ttf", 50
)
clock: pygame.time.Clock = pygame.time.Clock()
