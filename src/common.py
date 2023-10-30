import math
import os
import sys
import time
import typing as t

import pygame


# for pyinstaller compat, input relative path, get out absolute path
def get_path(filename: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)  # type: ignore
    else:
        return filename


def scale_add(img: pygame.Surface, term: float | int) -> pygame.Surface:
    return pygame.transform.scale(
        img, (img.get_width() + term, img.get_height() + term)
    )


def render_at(
    base_surf: pygame.Surface,
    surf: pygame.Surface,
    pos: str,
    offset: t.Sequence = (0, 0),
) -> None:
    """Renders a surface to a base surface by matching a point.

    Example: render_at(screen, widget, "center")
    """
    base_rect = base_surf.get_rect()
    surf_rect = surf.get_rect()
    setattr(surf_rect, pos, getattr(base_rect, pos))
    surf_rect.x += offset[0]
    surf_rect.y += offset[1]
    base_surf.blit(surf, surf_rect)


class Time:
    """Class to check if a certain amount of time has passed."""

    def __init__(self, time_to_pass: float):
        self.time_to_pass = time_to_pass
        self.start = time.perf_counter()

    def reset(self):
        self.start = time.perf_counter()

    def tick(self) -> bool:
        if time.perf_counter() - self.start > self.time_to_pass:
            self.start = time.perf_counter()
            return True
        return False


class SinWave:
    def __init__(self, speed):
        self.speed = speed
        self.radians = 0
        self.val = 0

    def update(self, dt: float):
        self.radians += self.speed * dt
        self.radians %= math.pi * 2
        self.val = math.sin(self.radians)
