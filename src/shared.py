from __future__ import annotations

import typing
from pathlib import Path

import pygame

import pytmx

from .enums import DoorDirection

if typing.TYPE_CHECKING:
    from .entities import Entity, Monster, Player

# Constants
ASSETS_PATH = Path("assets/")
ART_PATH = ASSETS_PATH / "art"
DATA_PATH = ASSETS_PATH / "data"
ROOMS_PATH = DATA_PATH / "rooms"

ENTITY_SPEED = 250.0
WIN_WIDTH = 1200.0
WIN_HEIGHT = 650.0
WIN_SIZE = (WIN_WIDTH, WIN_HEIGHT)
TILE_SIDE = 64
TILE_SIZE = (TILE_SIDE, TILE_SIDE)

# Shared variables
room_map: pytmx.TiledMap
rows: int
cols: int
screen: pygame.Surface
clock: pygame.Clock
events: list[pygame.event.Event]
keys: list[bool]
dt: float
mouse_pos: pygame.Vector2
camera_pos: pygame.Vector2
room_id: int = 1
monster_room: int = 9
monster_last_room: int = -1
monster_move_chance: float = 1  # 5% chance
monster_move_time: int = 1  # every x seconds
entities: list[Entity]
player: Player
monster: Monster | None = None
next_door = DoorDirection.SOUTH
overlay: pygame.Surface
game_name: str = "Title"
