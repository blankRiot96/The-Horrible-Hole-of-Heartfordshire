import pygame

from . import shared
from .asset_loader import Loader
from .button import Button
from .gamestate import GameState, GameStateManager


def set_reset_flag() -> None:
    shared.reset = True


def start_game() -> None:
    set_reset_flag()
    if shared.menu_audio is not None:
        shared.menu_audio.stop()


def quit() -> None:
    raise SystemExit


class MainMenu(GameState):
    def __init__(self) -> None:
        super().__init__("MainMenu")
        self.font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 60)
        self.buttons = [
            Button(
                pygame.Vector2(shared.screen.get_rect().center)
                - pygame.Vector2(0, 100),
                start_game,
                self.font,
                "Start Game",
                shared.TEXT_COLORS[0],
                shared.BUTTON_COLOR,
                shared.BORDER_COLOR,
            ),
            Button(
                pygame.Vector2(shared.screen.get_rect().center),
                lambda: GameStateManager().set_state("IntroState"),
                self.font,
                "Replay Intro",
                shared.TEXT_COLORS[1],
                shared.BUTTON_COLOR,
                shared.BORDER_COLOR,
            ),
        ]
        if not shared.IS_WASM:
            self.buttons.append(
                Button(
                    pygame.Vector2(shared.screen.get_rect().center)
                    + pygame.Vector2(0, 100),
                    quit,
                    self.font,
                    "Quit",
                    shared.TEXT_COLORS[2],
                    shared.BUTTON_COLOR,
                    shared.BORDER_COLOR,
                ),
            )
        self.title = self.font.render(shared.game_name, True, "White")
        if shared.menu_audio is not None and not shared.menu_audio.get_num_channels():
            shared.menu_audio.play(-1)

        self.bg = pygame.transform.scale(
            pygame.image.load(shared.ART_PATH / "bricks.png").convert_alpha(),
            shared.WIN_SIZE,
        )

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
        shared.screen.blit(self.bg, (0, 0))
        shared.screen.blit(
            self.title, self.title.get_rect(midtop=shared.screen.get_rect().midtop)
        )
        for button in self.buttons:
            button.draw()
