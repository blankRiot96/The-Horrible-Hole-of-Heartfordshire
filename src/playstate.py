import pygame
import pytmx

from . import shared
from .gamestate import GameState
from .grid import Grid


def load_room():
    """Loads room from rood ID"""
    shared.room_map = pytmx.load_pygame(shared.ROOMS_PATH / f"{shared.room_id}.tmx")
    shared.rows = shared.room_map.height
    shared.cols = shared.room_map.width


class PlayState(GameState):
    def __init__(self) -> None:
        super().__init__("PlayState")
        load_room()
        self.grid = Grid()
        self.grid.load_entities_from_room()
        shared.camera_pos = pygame.Vector2()

    def handle_events(self) -> None:
        ...

    def update(self):
        self.grid.update()
        shared.camera_pos.move_towards_ip(shared.player.rect.center, 1000 * shared.dt)

    def draw(self):
        self.grid.draw()
