import random

import pygame

import pytmx

from . import shared
from .common import Time
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
        self.monster_timer = Time(30)

    def handle_events(self) -> None:
        ...

    def handle_camera(self) -> None:
        shared.camera_pos.move_towards_ip(
            shared.player.rect.center, self.cam_speed * shared.dt
        )
        self.cam_speed = (shared.ENTITY_SPEED * 0.65) * (
            shared.camera_pos.distance_to(shared.player.rect.center) / 75
        )

    def check_monster_move(self) -> None:
        if not self.monster_timer.tick():
            return

        will_change = random.random() < shared.monster_move_chance
        if will_change:
            options = [shared.monster_room + diff for diff in [1, -1, 3, -3]]
            options = [op for op in options if 0 < op < 10]
            shared.monster_room = random.choice(options)

    def update(self) -> None:
        self.grid.update()
        self.handle_camera()
        if shared.monster_room != shared.room_id:
            self.check_monster_move()

    def draw(self) -> None:
        shared.overlay.fill("black")
        self.grid.draw()
        shared.screen.blit(shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
