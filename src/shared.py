from __future__ import annotations

import sys
import typing
from pathlib import Path

import pygame

import pytmx

from .enums import DoorDirection

if typing.TYPE_CHECKING:
    from .entities import Entity, Player
    from .graph import Graph
    from .monster_manager import Monster

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
# MAZE_ROOMS = (3, 5, 7)
MAZE_ROOMS = (3, 7)
COMB_LOCK_ROOMS = (2, 5, 4, 9)

IS_WASM = sys.platform == "emscripten"

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
entities: list[Entity]
cells: list[pygame.Vector2]
player: Player
monster: Monster
next_door = DoorDirection.SOUTH
overlay: pygame.Surface
game_name: str = "The Horrible Hole of Hertfordshire"
entities_in_room: dict[int, list[Entity]] = {}
reset: bool = False
check_solve: bool = False
graph: Graph
update_graph: bool = True
menu_audio: pygame.mixer.Sound | None = None
game_audio: pygame.mixer.Sound | None = None
monster_audio: pygame.mixer.Sound | None = None
win: bool = False

# colors
BUTTON_COLOR = (89, 86, 82)
BORDER_COLOR = (0, 0, 0)
TEXT_COLORS = ((106, 190, 48), (0, 0, 0), (172, 50, 50))

WHITE = (172, 50, 50)
