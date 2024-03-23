from pathlib import Path

import pygame

pygame.font.init()

total_ticks: int = 0

font: pygame.font.Font = pygame.font.Font(
    Path(__file__).parent / "fonts" / "playpen_sans" / "PlaypenSans-Regular.ttf", 50
)
clock: pygame.time.Clock = pygame.time.Clock()
