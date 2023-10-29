from itertools import cycle
from pathlib import Path
from typing import Sequence

import pygame

from .common import Time


def get_frames(
    path: Path, size: tuple[int, int], alpha: bool = True
) -> list[pygame.Surface]:
    img = pygame.image.load(path)
    if alpha:
        img = img.convert_alpha()
    else:
        img = img.convert()

    img_width, img_height = img.get_size()
    width, height = size

    rows = img_height // height
    cols = img_width // width

    frames = []
    for row in range(rows):
        for col in range(cols):
            frame = img.subsurface((col * width, row * height, width, height))
            frames.append(frame)

    return frames


class Animation:
    def __init__(
        self, frames: Sequence[pygame.Surface], animation_cooldown: float
    ) -> None:
        self.indexable_frames = tuple(frames)
        self.frames = cycle(frames)
        self.animation_cooldown = animation_cooldown
        self.timer = Time(self.animation_cooldown)
        self.current_frame = next(self.frames)

    def update(self):
        if self.timer.tick():
            self.current_frame = next(self.frames)
