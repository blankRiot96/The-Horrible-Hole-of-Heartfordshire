import pygame

import pytmx

from . import shared
from .entities import Stone
from .gamestate import GameState
from .grid import Grid


def load_room():
    """Loads room from room ID"""
    shared.room_map = pytmx.load_pygame(shared.ROOMS_PATH / f"{shared.room_id}.tmx")  # type: ignore
    shared.rows = shared.room_map.height
    shared.cols = shared.room_map.width


class PlayState(GameState):
    def __init__(self) -> None:
        super().__init__("PlayState")
        load_room()
        self.grid = Grid()
        self.grid.load_entities_from_room()
        shared.camera_pos = pygame.Vector2(shared.player.rect.center)
        self.cam_speed = shared.ENTITY_SPEED * 0.65
        shared.overlay = pygame.Surface(shared.WIN_SIZE)

    def handle_events(self) -> None:
        ...

    def handle_camera(self) -> None:
        shared.camera_pos.move_towards_ip(
            shared.player.rect.center, self.cam_speed * shared.dt
        )
        self.cam_speed = (shared.ENTITY_SPEED * 0.65) * (
            shared.camera_pos.distance_to(shared.player.rect.center) / 75
        )

    def update(self) -> None:
        self.grid.update()
        self.handle_camera()

    def draw(self) -> None:
        shared.overlay.fill("black")
        self.grid.draw()
        shared.screen.blit(shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
