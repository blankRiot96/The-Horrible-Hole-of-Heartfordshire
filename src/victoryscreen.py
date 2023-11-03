from math import ceil

import pygame

from . import shared
from .anim import get_frames
from .asset_loader import Loader
from .button import Button
from .common import Time, get_path
from .gamestate import GameState, GameStateManager


def set_reset_flag():
    if (
        VictoryScreen.victory_audio is not None
        and VictoryScreen.victory_audio.get_num_channels()
    ):
        VictoryScreen.victory_audio.stop()
    shared.reset = True


def main_menu():
    if (
        VictoryScreen.victory_audio is not None
        and VictoryScreen.victory_audio.get_num_channels()
    ):
        VictoryScreen.victory_audio.stop()
    GameStateManager().set_state("MainMenu")


class VictoryScreen(GameState):
    victory_audio: pygame.mixer.Sound | None = None

    def __init__(self) -> None:
        super().__init__("VictoryScreen")
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
                main_menu,
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

        self.victory_message = self.death_font.render(
            "You have survived!", True, "gold"
        )

        self.spritesheet = pygame.image.load(
            shared.ART_PATH / "tileset-64.png"
        ).convert_alpha()
        floor_rect = pygame.Rect(128, 128, 64, 64)
        wall_rect = pygame.Rect(128, 192, 64, 128)
        door_rect = pygame.Rect(192, 512, 192, 128)
        self.floor_tile = self.spritesheet.subsurface(floor_rect)
        self.wall_tile = self.spritesheet.subsurface(wall_rect)
        self.door = self.spritesheet.subsurface(door_rect)

        self.bg = pygame.Surface(shared.WIN_SIZE)
        rows = ceil(shared.WIN_HEIGHT / shared.TILE_SIDE)
        cols = ceil(shared.WIN_WIDTH / shared.TILE_SIDE)
        for row in range(rows):
            for col in range(cols):
                pos = col * shared.TILE_SIDE, row * shared.TILE_SIDE
                self.bg.blit(self.floor_tile, pos)

        for col in range(cols):
            pos = col * shared.TILE_SIDE, (rows - 3) * shared.TILE_SIDE + 10
            self.bg.blit(self.wall_tile, pos)

        self.bg.blit(
            self.door, self.door.get_rect(midbottom=self.bg.get_rect().midbottom)
        )
        self.player_frames = get_frames(shared.ART_PATH / "player-128.png", (64, 128))[
            :4
        ]
        self.player_rect = self.player_frames[0].get_frect(
            center=shared.screen.get_rect().center
        )

        self.frame_index = 0
        self.frame_timer = Time(0.1)
        self.current_frame = self.player_frames[0]

        self.animation_done = False

        if shared.game_audio is not None and shared.game_audio.get_num_channels():
            shared.game_audio.stop()

        if VictoryScreen.victory_audio is None:
            VictoryScreen.victory_audio = Loader().get_sound(
                get_path("assets/audio/hhhmenumotif.ogg")
            )

        if not VictoryScreen.victory_audio.get_num_channels():
            VictoryScreen.victory_audio.play(-1)

    def handle_events(self) -> None:
        if self.animation_done:
            for event in shared.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in self.buttons:
                            if button.rect.collidepoint(shared.mouse_pos):
                                button.click()

    def update(self) -> None:
        if not self.animation_done:
            if self.frame_timer.tick():
                self.frame_index = (self.frame_index + 1) % len(self.player_frames)
            self.player_rect.move_ip(0, shared.dt * shared.ENTITY_SPEED)

        if self.player_rect.top >= shared.screen.get_rect().bottom:
            self.animation_done = True

    def draw(self) -> None:
        shared.screen.blit(self.bg, (0, 0))
        if self.animation_done:
            shared.screen.blit(
                self.victory_message,
                self.victory_message.get_rect(midtop=shared.screen.get_rect().midtop),
            )
            for button in self.buttons:
                button.draw()

        else:
            shared.screen.blit(self.player_frames[self.frame_index], self.player_rect)
