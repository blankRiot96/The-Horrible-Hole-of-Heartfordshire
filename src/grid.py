import pygame

from . import shared
from .entities import Door, Player, Stone, Torch, Wall


class Grid:
    LINE_COLOR = "black"

    ENTITIES = {0: Door, 1: Player, 2: Stone, 3: Wall, 7: Torch}

    def __init__(self) -> None:
        shared.entities = []

    def add_entity(self, entity):
        shared.entities.append(entity)

    def update(self):
        for entity in shared.entities:
            entity.update()

    def place_entity(
        self, row, col, entity_no, image: pygame.Surface, properties: dict
    ):
        entity = Grid.ENTITIES.get(entity_no)
        if entity is None:
            return
        self.add_entity(entity((col, row), image, properties))

    def load_entities_from_room(self) -> None:
        for layer in shared.room_map.layers:
            for x, y, image in layer.tiles():
                gid = layer.data[y][x]
                properties = shared.room_map.get_tile_properties_by_gid(gid)
                entity_id = properties["id"]
                self.place_entity(
                    y, x, entity_no=entity_id, image=image, properties=properties
                )

    def draw_grid(self):
        for row in range(shared.rows + 1):
            start = 0, row * shared.TILE_SIDE
            end = shared.WIN_WIDTH, row * shared.TILE_SIDE
            pygame.draw.line(shared.screen, Grid.LINE_COLOR, start, end)

        for col in range(shared.cols + 1):
            start = col * shared.TILE_SIDE, 0
            end = col * shared.TILE_SIDE, shared.WIN_HEIGHT
            pygame.draw.line(shared.screen, Grid.LINE_COLOR, start, end)

    def draw(self):
        # self.draw_grid()
        for entity in shared.entities:
            entity.draw()
