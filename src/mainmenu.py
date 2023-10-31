import pygame

from . import shared
from .asset_loader import Loader
from .button import Button
from .gamestate import GameState, GameStateManager


class MainMenu(GameState):
    def __init__(self) -> None:
        super().__init__("MainMenu")
        self.font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 60)
        self.buttons = [
            Button(
                pygame.Vector2(shared.screen.get_rect().center),
                lambda: GameStateManager().set_state("PlayState"),
                self.font,
                "Start Game",
                "red",
                "blue",
                "green",
            )
        ]
        self.title = self.font.render(shared.game_name, True, "White")

    def handle_events(self) -> None:
        for event in shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons:
                        if button.rect.collidepoint(shared.mouse_pos):
                            button.click()

    def update(self) -> None:
        ...

    def draw(self) -> None:
        shared.screen.blit(
            self.title, self.title.get_rect(midtop=shared.screen.get_rect().midtop)
        )
        for button in self.buttons:
            button.draw()
