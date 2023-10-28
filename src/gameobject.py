import pygame

from . import shared


def get_relative_pos(absolute_pos: pygame.Vector2) -> pygame.Vector2:
    camera_origin = shared.camera_pos - pygame.Vector2(
        shared.screen.get_width() / 2, shared.screen.get_height() / 2
    )

    return absolute_pos - camera_origin


def get_absolute_pos(relative_pos: pygame.Vector2) -> pygame.Vector2:
    camera_origin = shared.camera_pos - pygame.Vector2(
        shared.screen.get_width() / 2, shared.screen.get_height() / 2
    )

    return relative_pos + camera_origin


class GameObject:
    def __init__(
        self,
        pos: pygame.Vector2,
        is_visible: bool,
        is_interactable: bool,
        image: pygame.Surface | None,
    ) -> None:
        # self.pos is the absolute position of the GameObject. Blitting will take shared.camera into account
        self.pos = pos
        self.is_visible = is_visible
        self.is_interactable = is_interactable
        self.image = image

    def move(self, offset: pygame.Vector2) -> None:
        self.pos += offset

    def draw(self) -> None:
        if self.is_visible and self.image is not None:
            shared.screen.blit(
                self.image, self.image.get_rect(topleft=get_relative_pos(self.pos))
            )
