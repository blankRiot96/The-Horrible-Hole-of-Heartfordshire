import pygame

from . import shared
from ._types import ColorValue
from .common import SinWave, scale_add
from .gameobject import get_relative_pos


class Bloom:
    IMAGE = pygame.image.load(shared.ART_PATH / "light.png").convert_alpha()

    def __init__(
        self,
        size: tuple[int, int],
        wave_speed: float,
        expansion_factor: int,
        layers: list[ColorValue] | None = None,
    ) -> None:
        self.size = size
        self.original_surf = pygame.transform.scale(Bloom.IMAGE, size)
        self.surf = self.original_surf.copy()
        self.rect = self.surf.get_rect()
        self.wave = SinWave(wave_speed)
        self.expansion_factor = expansion_factor
        self.layers = layers

        self.draw_surf()

    def draw_surf(self):
        if self.layers is None:
            return

        width_delta = self.size[0] / len(self.layers)
        height_delta = self.size[0] / len(self.layers)
        layer_bases = []
        for layer, layer_color in enumerate(self.layers):
            layer += 1
            width, height = width_delta * layer, height_delta * layer
            layer_base = pygame.transform.scale(Bloom.IMAGE, (width, height))
            layer_surf = pygame.Surface((width, height))
            layer_surf.fill(layer_color)
            layer_base.blit(layer_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            layer_bases.append(layer_base)

        for layer_base in reversed(layer_bases):
            self.original_surf.blit(
                layer_base,
                layer_base.get_rect(center=self.original_surf.get_rect().center),
                # special_flags=pygame.BLEND_RGBA_ADD,
            )

    def update(self, pos):
        self.wave.update(shared.dt)
        self.surf = scale_add(self.original_surf, self.wave.val * self.expansion_factor)
        self.rect = self.surf.get_rect()
        self.rect.center = pos

    def draw(self):
        shared.overlay.blit(
            self.surf,
            get_relative_pos(self.rect.topleft),
            # special_flags=pygame.BLEND_RGBA_SUB,
        )
