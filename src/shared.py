from pathlib import Path

import pygame
import pytmx

from .enums import DoorDirection

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
entities: list
player: object
next_door = DoorDirection.SOUTH
