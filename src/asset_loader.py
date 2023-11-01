from __future__ import annotations

from pathlib import Path

import pygame

from .common import get_path


class Loader:
    __instance = None
    __fonts: dict[tuple[str, int], pygame.Font] = {}
    __sounds: dict[str, pygame.mixer.Sound] = {}

    def __new__(cls) -> Loader:
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def get_sound(self, filename: str) -> pygame.mixer.Sound:
        if filename not in self.__sounds:
            self.__sounds[filename] = pygame.mixer.Sound(get_path(filename))
        return self.__sounds[filename]

    def remove_sound(self, filename: str) -> None:
        if filename in self.__sounds:
            del self.__sounds[filename]

    def get_font(self, filename: str, font_size: int = 20) -> pygame.Font:
        if (filename, font_size) not in self.__fonts:
            self.__fonts[filename, font_size] = pygame.Font(
                get_path(filename), font_size
            )
        return self.__fonts[filename, font_size]

    def remove_font(self, filename: str, font_size: int = 20) -> None:
        if (filename, font_size) in self.__fonts:
            del self.__fonts[filename, font_size]
