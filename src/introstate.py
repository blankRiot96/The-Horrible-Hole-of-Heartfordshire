from glob import glob

import pygame

from . import shared
from .asset_loader import Loader
from .common import Time, get_path
from .gamestate import GameState, GameStateManager


class IntroState(GameState):
    def __init__(self) -> None:
        super().__init__("IntroState")
        self.font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 30)
        self.scenes: dict[int, tuple[str, int]] = {}
        self.load_scenes()
        self.current_scene = 1
        self.character_index = 0
        self.character_delay = 0.1  # seconds
        self.character_timer = Time(self.character_delay)
        self.ready_to_continue = False

    def load_scenes(self) -> None:
        scene_files = glob(get_path("assets/intro/*.txt"))
        for file in scene_files:
            number = int(file.split(".")[-2].split("_")[-1])
            with open(file, "r") as scene:
                text = scene.read()
                self.scenes[number] = text, len(text.split("(Press any key")[0])

    def is_last_scene(self) -> bool:
        return self.current_scene == max(self.scenes.keys())

    def move_to_next_scene(self) -> None:
        self.character_timer.reset()
        self.ready_to_continue = False
        self.current_scene += 1
        self.character_index = 0

    def increment_character(self) -> None:
        if self.character_index < len(self.scenes[self.current_scene][0]):
            if self.character_index == self.scenes[self.current_scene][1]:
                self.character_index = len(self.scenes[self.current_scene][0])
            if self.character_timer.tick():
                self.character_index += 1
        else:
            self.ready_to_continue = True

    def handle_events(self) -> None:
        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                if self.ready_to_continue:
                    if not self.is_last_scene():
                        self.move_to_next_scene()
                    else:
                        GameStateManager().set_state("PlayState")

    def update(self) -> None:
        if shared.keys[pygame.K_SPACE]:
            self.character_delay = 0.05
        else:
            self.character_delay = 0.1
        self.character_timer.time_to_pass = self.character_delay
        self.increment_character()

    def draw(self) -> None:
        text = self.scenes[self.current_scene][0][: self.character_index]
        rendered = self.font.render(
            text, True, "white", wraplength=shared.screen.get_width()
        )

        shared.screen.blit(rendered, (0, 0))
