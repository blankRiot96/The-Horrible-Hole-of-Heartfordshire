import pygame

from . import shared
from .entities import Player, Stone


class Grid:
    LINE_COLOR = "black"

    ENTITIES = {1: Player, 2: Stone}

    def __init__(self) -> None:
        shared.entities: list = []

    def add_entity(self, entity):
        shared.entities.append(entity)

    def update(self):
        for entity in shared.entities:
            entity.update()

    def place_entity(self, row, col, entity_no):
        entity = Grid.ENTITIES.get(entity_no)
        if entity is None:
            return
        self.add_entity(entity((col, row)))

    def draw_grid(self):
        for row in range(shared.ROWS + 1):
            start = 0, row * shared.TILE_SIDE
            end = shared.WIN_WIDTH, row * shared.TILE_SIDE
            pygame.draw.line(shared.screen, Grid.LINE_COLOR, start, end)

        for col in range(shared.COLS + 1):
            start = col * shared.TILE_SIDE, 0
            end = col * shared.TILE_SIDE, shared.WIN_HEIGHT
            pygame.draw.line(shared.screen, Grid.LINE_COLOR, start, end)

    def draw(self):
        self.draw_grid()
        for entity in shared.entities:
            entity.draw()
