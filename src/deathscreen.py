import pygame

from . import shared
from .anim import get_frames
from .asset_loader import Loader
from .button import Button
from .common import Time, get_path
from .gamestate import GameState, GameStateManager


def set_reset_flag():
    shared.reset = True


class DeathScreen(GameState):
    death_audio: pygame.mixer.Sound | None = None
    frames: list[pygame.Surface] = []

    def __init__(self) -> None:
        super().__init__("DeathScreen")
        self.frame_timer = Time(0.10)

        self.button_font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 60)
        self.death_font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 120)
        self.buttons = [
            Button(
                pygame.Vector2(shared.screen.get_rect().center),
                set_reset_flag,
                self.button_font,
                "New Game",
                shared.TEXT_COLORS[0],
                shared.BUTTON_COLOR,
                shared.BORDER_COLOR,
            ),
            Button(
                pygame.Vector2(shared.screen.get_rect().center)
                + pygame.Vector2(0, 100),
                lambda: GameStateManager().set_state("MainMenu"),
                self.button_font,
                "Main Menu",
                shared.TEXT_COLORS[1],
                shared.BUTTON_COLOR,
                shared.BORDER_COLOR,
            ),
        ]
        if not shared.IS_WASM:
            self.buttons.append(
                Button(
                    pygame.Vector2(shared.screen.get_rect().center)
                    + pygame.Vector2(0, 200),
                    quit,
                    self.button_font,
                    "Quit",
                    shared.TEXT_COLORS[2],
                    shared.BUTTON_COLOR,
                    shared.BORDER_COLOR,
                ),
            )
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

        if not DeathScreen.frames:
            DeathScreen.frames = get_frames(
                get_path("assets/art/shadowdeath.png"), (150, 80)
            )
            for idx, frame in enumerate(DeathScreen.frames):
                DeathScreen.frames[idx] = pygame.transform.scale(frame, shared.WIN_SIZE)
        self.frame_index = 0
        self.animation_finished = False

    def handle_events(self) -> None:
        for event in shared.events:
            if not self.animation_finished:
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons:
                        if button.rect.collidepoint(shared.mouse_pos):
                            button.click()

    def update(self) -> None:
        ...

    def draw(self) -> None:
        if self.frame_index < len(DeathScreen.frames):
            if self.frame_timer.tick():
                self.frame_index += 1
        else:
            self.animation_finished = True

        display_frame_index = min(self.frame_index, len(DeathScreen.frames) - 1)
        shared.screen.blit(DeathScreen.frames[display_frame_index], (0, 0))
        if self.animation_finished:
            shared.screen.blit(
                self.death_message,
                self.death_message.get_rect(midtop=shared.screen.get_rect().midtop),
            )
            for button in self.buttons:
                button.draw()
