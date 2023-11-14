import pygame

import pytmx

from . import shared
from .asset_loader import Loader
from .button import Button
from .combination_lock import CombinationLock
from .common import get_path
from .entities import Door, Hole, Stone, Torch
from .enums import DoorDirection
from .gamestate import GameState, GameStateManager
from .grid import Grid
from .monster_manager import MonsterManager
from .puzzle_manager import PuzzleManager


def load_room():
    """Loads room from room ID"""
    shared.room_map = pytmx.load_pygame(get_path(f"assets/data/rooms/{shared.room_id}.tmx"))  # type: ignore
    shared.rows = shared.room_map.height
    shared.cols = shared.room_map.width


class PlayState(GameState):
    DEBUG_ROOM = 8

    def __init__(self) -> None:
        super().__init__("PlayState")

        self.game_init()
        self.audio_init()
        self.debug_init()
        # self.debug_printing()

    def debug_printing(self):
        print("-" * 10)
        print(shared.room_id)
        print()
        for entity in shared.entities:
            if isinstance(entity, Door):
                print(entity.locked, entity.cell)
        print("-" * 10)

    def game_init(self):
        load_room()
        self.monster_manager = MonsterManager()
        self.grid = Grid()
        shared.camera_pos = pygame.Vector2(shared.player.rect.center)
        self.cam_speed = shared.ENTITY_SPEED * 0.65
        shared.overlay = pygame.Surface(shared.WIN_SIZE)
        self.puzzle_manager = PuzzleManager()
        self.comb_lock = CombinationLock()
        shared.update_graph = True

    def audio_init(self):
        if shared.game_audio is None:
            shared.game_audio = Loader().get_sound(
                get_path("assets/audio/hhhdungeon.ogg")
            )
        if not shared.game_audio.get_num_channels():
            shared.game_audio.play(-1, 0, 1_000)

    def debug_init(self):
        self.debug_font = Loader().get_font("assets/font/DotGothic16-Regular.ttf", 32)

        self.buttons = [
            Button(
                pygame.Vector2(100, 30),
                self.on_solve,
                self.debug_font,
                "Solve",
                text_color="white",
                background_color="green",
                border_color="white",
            ),
            Button(
                pygame.Vector2(120, 90),
                self.on_teleport,
                self.debug_font,
                f"Teleport to {PlayState.DEBUG_ROOM}",
                text_color="white",
                background_color="red",
                border_color="white",
            ),
        ]

    def solve_stone(self, stone: Stone):
        for entity in shared.entities:
            if isinstance(entity, Hole) and entity.symbol == stone.symbol:
                stone.desired_cell = entity.cell
                stone.speed = 600.0

    def on_solve(self):
        if shared.room_id in shared.MAZE_ROOMS:
            return

        if shared.room_id in shared.COMB_LOCK_ROOMS and shared.room_id not in (4, 9):
            for entity in shared.entities:
                if isinstance(entity, Torch):
                    entity.lit = True

        for entity in shared.entities:
            if isinstance(entity, Stone):
                self.solve_stone(entity)

        shared.check_solve = True

    def on_teleport(self):
        shared.entities_in_room[shared.room_id] = shared.entities.copy()
        shared.room_id = PlayState.DEBUG_ROOM

        shared.next_door = DoorDirection.NORTH
        GameStateManager().set_state("PlayState")

    def handle_events(self) -> None:
        for event in shared.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and not shared.monster.chasing:
                    GameStateManager().set_state("PlayState")

    def handle_camera(self) -> None:
        shared.camera_pos.move_towards_ip(
            shared.player.rect.center, self.cam_speed * shared.dt
        )
        self.cam_speed = (shared.ENTITY_SPEED * 0.65) * (
            shared.camera_pos.distance_to(shared.player.rect.center) / 75
        )

    def stop_monster_audio_if_not_chasing(self) -> None:
        if (
            not shared.monster.chasing
            and shared.monster_audio is not None
            and shared.monster_audio.get_num_channels()
        ):
            shared.monster_audio.stop()

    def update_buttons(self):
        for button in self.buttons:
            button.update()

    def update(self) -> None:
        self.update_buttons()
        self.stop_monster_audio_if_not_chasing()
        self.grid.update()
        self.handle_camera()
        self.monster_manager.update()
        self.puzzle_manager.update()
        self.comb_lock.update()

    def draw_buttons(self):
        for button in self.buttons:
            button.draw()

    def draw(self) -> None:
        shared.overlay.fill("black")
        self.grid.draw()
        self.monster_manager.draw()
        self.puzzle_manager.draw()
        shared.screen.blit(
            shared.overlay.subsurface(shared.screen.get_rect()),
            (0, 0),
            special_flags=pygame.BLEND_RGBA_MIN,
        )
        self.comb_lock.draw()
        self.draw_buttons()
