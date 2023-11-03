import pygame

import pytmx

from . import shared
from .combination_lock import CombinationLock
from .gamestate import GameState, GameStateManager
from .grid import Grid
from .monster_manager import MonsterManager
from .puzzle_manager import PuzzleManager


def load_room():
    """Loads room from room ID"""
    shared.room_map = pytmx.load_pygame(shared.ROOMS_PATH / f"{shared.room_id}.tmx")  # type: ignore
    shared.rows = shared.room_map.height
    shared.cols = shared.room_map.width


class PlayState(GameState):
    def __init__(self) -> None:
        super().__init__("PlayState")
        load_room()
        self.monster_manager = MonsterManager()
        self.grid = Grid()
        shared.camera_pos = pygame.Vector2(shared.player.rect.center)
        self.cam_speed = shared.ENTITY_SPEED * 0.65
        shared.overlay = pygame.Surface(shared.WIN_SIZE)
        self.puzzle_manager = PuzzleManager()
        self.comb_lock = CombinationLock()
        shared.update_graph = True

    def handle_events(self) -> None:
        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                #  this is purely for testing purposes
                # if event.key == pygame.K_ESCAPE:
                #     GameStateManager().set_state("DeathScreen")
                if event.key == pygame.K_r:
                    GameStateManager().set_state("PlayState")

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
        self.monster_manager.update()
        self.puzzle_manager.update()
        self.comb_lock.update()

    def draw(self) -> None:
        shared.overlay.fill("black")
        self.grid.draw()
        self.monster_manager.draw()
        # shared.screen.blit(shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.puzzle_manager.draw()
        shared.screen.blit(shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.comb_lock.draw()
