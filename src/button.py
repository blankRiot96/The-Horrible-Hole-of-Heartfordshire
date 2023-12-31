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

        rect = self.text.get_rect()
        rect.size += pygame.Vector2(20, 0)

        self.surf = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
        pygame.draw.rect(self.surf, background_color, rect, border_radius=10)
        pygame.draw.rect(self.surf, border_color, rect, 2, border_radius=10)
        self.surf.blit(self.text, (10, 0))

        self.rect = rect.copy()
        self.rect.center = self.pos

        self.hovering = False
        self.clicked = False

    def click(self) -> None:
        self._callback()

    def on_click(self):
        self.clicked = False
        for event in shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.clicked = True

    def update(self):
        self.hovering = self.rect.collidepoint(shared.mouse_pos)
        self.on_click()

        if self.clicked and self.hovering:
            self.click()

    def draw(self) -> None:
        shared.screen.blit(self.surf, self.rect)
