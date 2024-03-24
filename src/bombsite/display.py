from typing import Optional

import numpy as np
import numpy.typing as npt
import pygame

from bombsite import logger, settings, ticks
from bombsite.world import playing_field


class Display:
    def __init__(self) -> None:
        """Creates the Pygame display."""
        self.screen: pygame.Surface = self.get_screen()
        self.x: float = 0
        self.vx: float = 0
        self.y: float = 0
        self.vy: float = 0
        self.focus: Optional[npt.NDArray[np.int_]] = None

    @staticmethod
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

    def set_focus(self, x: int, y: int) -> None:
        """Sets a new focus so that the display will pan to it.

        Args:
            x: The x-position of the focus.
            y: The y-position of the focus.
        """
        self.focus = np.array((x, y))

    def update_display(self, pf: playing_field.PlayingField) -> None:
        """Fills in the background, draws the map image, and updates the
        display.

        Args:
            pf: The playing field the display shows.
        """
        self.screen.fill(pygame.Color("lightblue"))

        self.screen.blit(pf.image, (-self.x, -self.y))
        for character in pf.characters:
            character.draw(self)

        for projectile in pf.projectiles:
            pygame.draw.circle(self.screen, pygame.Color("black"), projectile.pos - self.pos, 2)

        logger.logger.draw(self.screen)

        if pf.game_state.controlled_can_attack:
            countdown = int(pf.time_left_on_clock())
            image = ticks.font.render(str(countdown), 1, pygame.Color("black"))
            self.screen.blit(image, (settings.SCREEN_WIDTH / 2 - image.get_width() / 2, 0))

        pygame.display.flip()

    def get_top_left_focus_coords(self, pf: playing_field.PlayingField) -> tuple[float, float]:
        """Finds the coordinates of the desired top-left corner of the
        camera once it has centred the focus.

        Args:
            pf: The playing field on which the display applies.

        Returns:
            The x-coordinate and the y-coordinate of the top-left corner
            of the expected screen.
        """
        top_left_x = self.focus[0] - settings.SCREEN_WIDTH // 2
        top_left_y = self.focus[1] - settings.SCREEN_HEIGHT // 2

        if top_left_x < 0:
            top_left_x = 0
        elif top_left_x + settings.SCREEN_WIDTH > pf.mask.shape[0]:
            top_left_x = pf.mask.shape[0] - settings.SCREEN_WIDTH

        if top_left_y < 0:
            top_left_y = 0
        elif top_left_y + settings.SCREEN_HEIGHT > pf.mask.shape[1]:
            top_left_y = pf.mask.shape[1] - settings.SCREEN_HEIGHT

        return int(top_left_x), int(top_left_y)

    def approach_focus(self, pf: playing_field.PlayingField) -> None:
        """Moves the camera in the direction of the focus.

        Args:
            pf: The playing field on which the display applies.
        """
        if self.focus is None:
            return

        top_left_x, top_left_y = self.get_top_left_focus_coords(pf)

        if self.x < self.focus[0]:
            self.vx = min((self.vx + 0.1, (top_left_x - self.x) * 0.1))
        else:
            self.vx = max((self.vx - 0.1, (top_left_x - self.x) * 0.1))

        if self.y < self.focus[1]:
            self.vy = min((self.vy + 0.1, (top_left_y - self.y) * 0.1))
        else:
            self.vy = max((self.vy - 0.1, (top_left_y - self.y) * 0.1))

    def mouse_accelerate_camera(self) -> None:
        """Updates the rate at which the display's camera moves."""
        if self.focus is not None:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()

        if mouse_x < settings.SCROLL_BORDER:
            self.vx = max(
                (
                    -settings.MOUSE_CAMERA_SPEED,
                    self.vx - settings.MOUSE_CAMERA_ACCELERATION,
                )
            )

        elif mouse_x > settings.SCREEN_WIDTH - settings.SCROLL_BORDER:
            self.vx = min(
                (
                    settings.MOUSE_CAMERA_SPEED,
                    self.vx + settings.MOUSE_CAMERA_ACCELERATION,
                )
            )

        else:
            self.vx -= np.sign(self.vx) * settings.MOUSE_CAMERA_ACCELERATION
            if abs(self.vx) < settings.MOUSE_CAMERA_ACCELERATION:
                self.vx = 0.0

        if mouse_y < settings.SCROLL_BORDER:
            self.vy = max(
                (
                    -settings.MOUSE_CAMERA_SPEED,
                    self.vy - settings.MOUSE_CAMERA_ACCELERATION,
                )
            )

        elif mouse_y > settings.SCREEN_HEIGHT - settings.SCROLL_BORDER:
            self.vy = min(
                (
                    settings.MOUSE_CAMERA_SPEED,
                    self.vy + settings.MOUSE_CAMERA_ACCELERATION,
                )
            )

        else:
            self.vy -= np.sign(self.vy) * settings.MOUSE_CAMERA_ACCELERATION
            if abs(self.vy) < settings.MOUSE_CAMERA_ACCELERATION:
                self.vy = 0.0

    def update_camera_pos(self, pf: playing_field.PlayingField) -> None:
        """Updates the rate at which the display's camera moves.

        Args:
            pf: The playing field over which the camera moves.
        """
        pf_width, pf_height = pf.mask.shape
        self.x += self.vx
        self.y += self.vy

        if self.focus is not None:
            top_left_x, top_left_y = self.get_top_left_focus_coords(pf)

            if self.focus is not None and abs(self.x - top_left_x) < 0.1:
                self.x = top_left_x
                self.vx = 0.0

            if self.focus is not None and abs(self.y - top_left_y) < 0.1:
                self.y = top_left_y
                self.vy = 0.0

            if self.focus is not None and self.x == top_left_x and self.y == top_left_y:
                self.focus = None

        if self.x < 0.0:
            self.x = 0.0
            self.vx = 0.0
        elif self.x > pf_width - settings.SCREEN_WIDTH:
            self.x = pf_width - settings.SCREEN_WIDTH
            self.vx = 0.0

        if self.y < 0.0:
            self.y = 0.0
            self.vy = 0.0
        elif self.y > pf_height - settings.SCREEN_HEIGHT:
            self.y = pf_height - settings.SCREEN_HEIGHT
            self.vy = 0.0

    def update(self, pf: playing_field.PlayingField) -> None:
        """Updates the display.

        Args:
            pf: The playing field the display shows.
        """
        self.mouse_accelerate_camera()
        self.approach_focus(pf)
        self.update_camera_pos(pf)
        self.update_display(pf)

    @property
    def pos(self) -> npt.NDArray[np.int_]:
        return np.array((self.x, self.y)).astype(int)
