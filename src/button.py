from typing import Callable

import pygame

from . import shared
from ._types import ColorValue


class Button:
    def __init__(
        self,
        pos: pygame.Vector2,
        callback: Callable,
        font: pygame.Font,
        text: str,
        text_color: ColorValue,
        background_color: ColorValue,
        border_color: ColorValue,
    ) -> None:
        self.pos = pos
        self._callback = callback
        self.text = font.render(text, True, text_color)

        self.surf = pygame.Surface(self.text.get_size())
        self.rect = self.text.get_rect(center=self.pos)
        rect = self.surf.get_rect()
        pygame.draw.rect(self.surf, background_color, rect, border_radius=10)
        pygame.draw.rect(self.surf, border_color, rect, 2, border_radius=10)
        self.surf.blit(self.text, rect)

    def click(self) -> None:
        self._callback()

    def draw(self) -> None:
        shared.screen.blit(self.surf, self.rect)
