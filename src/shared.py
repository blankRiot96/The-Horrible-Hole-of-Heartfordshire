import pygame

# Constants
ROWS = 10
COLS = 20
TILE_SIDE = 64
TILE_SIZE = (TILE_SIDE, TILE_SIDE)
WIN_WIDTH = COLS * TILE_SIDE
WIN_HEIGHT = ROWS * TILE_SIDE
WIN_SIZE = (WIN_WIDTH + 2, WIN_HEIGHT + 2)
ENTITY_SPEED = 300.0


# Shared variables
screen: pygame.Surface
clock: pygame.Clock
events: list[pygame.event.Event]
keys: list[bool]
dt: float
mouse_pos: pygame.Vector2
camera_pos: pygame.Vector2
