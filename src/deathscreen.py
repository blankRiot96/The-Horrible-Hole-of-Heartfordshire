import pygame

from . import shared
from .asset_loader import Loader
from .button import Button
from .common import get_path
from .gamestate import GameState, GameStateManager


def set_reset_flag():
    shared.reset = True


class DeathScreen(GameState):
    death_audio: pygame.mixer.Sound | None = None

    def __init__(self) -> None:
        super().__init__("DeathScreen")
        self.button_font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 60)
        self.death_font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 120)
        self.buttons = [
            Button(
                pygame.Vector2(shared.screen.get_rect().center),
                set_reset_flag,
                self.button_font,
                "New Game",
                "red",
                "blue",
                "green",
            ),
            Button(
                pygame.Vector2(shared.screen.get_rect().center)
                + pygame.Vector2(0, 100),
                lambda: GameStateManager().set_state("MainMenu"),
                self.button_font,
                "Main Menu",
                "blue",
                "red",
                "green",
            ),
        ]
        self.death_message = self.death_font.render("You have died!", True, "Red")
        if shared.game_audio is not None and shared.game_audio.get_num_channels():
            shared.game_audio.stop()
        if shared.monster_audio is not None and shared.monster_audio.get_num_channels():
            shared.monster_audio.stop()
        if DeathScreen.death_audio is None:
            DeathScreen.death_audio = Loader().get_sound(
                get_path("assets/audio/hhhjumpscare.ogg")
            )
        if DeathScreen.death_audio.get_num_channels():
            DeathScreen.death_audio.stop()
        DeathScreen.death_audio.play()

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
            self.death_message,
            self.death_message.get_rect(midtop=shared.screen.get_rect().midtop),
        )
        for button in self.buttons:
            button.draw()
