import random

import pygame

from . import shared
from .asset_loader import Loader
from .common import Time


def _get_subsurface(img: pygame.Surface, y):
    wid = img.get_width()
    height = random.randrange(10, 20)
    shift = random.randint(10, 20)
    shift *= random.choice((1, -1))
    if y + height > img.get_height():
        height = img.get_height() - y

    sub = img.subsurface((0, y, wid, height))
    sub_rect = sub.get_rect()
    result = pygame.Surface(sub_rect.size)

    result.blit(sub, (shift, 0))
    if shift > 0:
        sub_shift = sub.subsurface((0, 0, wid - shift, height))
        result.blit(sub_shift, (0, 0))
    else:
        sub_shift = sub.subsurface(abs(shift), 0, wid - abs(shift), height)
        result.blit(sub_shift, (wid - abs(shift), 0))
    return result


def _get_full_glitched(img: pygame.Surface):
    y_travelled = 0
    result = img.copy()
    while y_travelled < img.get_height():
        if random.random() > 0.8:
            strip = _get_subsurface(img, y_travelled)
            y_travelled += strip.get_height()
            result.blit(strip, (0, y_travelled))
        else:
            y_travelled += random.randrange(10, 20)
    return result


class Glitch:
    def __init__(self) -> None:
        self.timer = Time(0.1)
        self.interval_timer = Time(0.3)
        self.image = shared.screen.copy()
        self.glitching = False
        self.dont_draw = True
        self.static_sfx = Loader().get_sound(shared.ASSETS_PATH / "audio/static.ogg")
        self.pause_over_time = 0.0

    def update(self):
        self.dont_draw = True
        if self.interval_timer.tick():
            self.glitching = not self.glitching
            if self.glitching:
                self.interval_timer.time_to_pass = random.uniform(0.2, 0.4)
            else:
                self.pause_over_time += 0.15
                if self.pause_over_time >= 2.0:
                    self.pause_over_time = 2.0
                self.interval_timer.time_to_pass = random.uniform(
                    0.5 + self.pause_over_time, 1.5 + self.pause_over_time
                )

    def draw(self):
        if (not self.glitching) and self.dont_draw:
            return
        if self.timer.tick():
            self.static_sfx.play()
            self.image = _get_full_glitched(shared.screen.copy())
            self.dont_draw = False
        shared.screen.blit(self.image, (0, 0))
