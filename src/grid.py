import pygame

from . import shared
from .entities import (
    Door,
    Entity,
    Foreground,
    Hole,
    MagicBlock,
    MagicHole,
    Pillar,
    Player,
    Stone,
    Torch,
    Wall,
)
from .enums import MovementType
from .gameobject import get_relative_pos


class Grid:
    LINE_COLOR = "black"

    ENTITIES = {
        "door": Door,
        "player": Player,
        "stone": Stone,
        "wall": Wall,
        "torch": Torch,
        "pillar": Pillar,
        "foreground": Foreground,
        "hole": Hole,
        "magic-block": MagicBlock,
        "magic-hole": MagicHole,
    }
    LOADED_BACKGROUNDS: dict[int, pygame.Surface] = {}

    def __init__(self) -> None:
        self.background = pygame.Surface(
            (
                shared.TILE_SIDE * shared.room_map.width,
                shared.TILE_SIDE * shared.room_map.height,
            ),
            pygame.SRCALPHA,
        )
        self.load_entities()

    def load_entities(self):
        saved_entities = shared.entities_in_room.get(shared.room_id)
        if saved_entities is None:
            shared.entities = []
            self.load_entities_from_room()
        else:
            shared.entities = saved_entities
            self.background = Grid.LOADED_BACKGROUNDS[shared.room_id]
            for i, entity in enumerate(shared.entities):
                if isinstance(entity, Player):
                    shared.entities[i] = shared.player
                    break
        self.align_player_pos()

    def add_entity(self, entity) -> None:
        shared.entities.append(entity)

    def remove_unused_entities(self) -> None:
        all_entities = shared.entities
        for entity in all_entities:
            if not entity.is_alive:
                shared.entities.remove(entity)

    def update(self) -> None:
        self.remove_unused_entities()
        for entity in shared.entities:
            entity.update()

    def place_entity(
        self, row, col, entity_id, image: pygame.Surface, properties: dict
    ) -> None:
        entity = Grid.ENTITIES.get(entity_id)
        if entity is None:
            self.background.blit(
                image, (col * shared.TILE_SIDE, row * shared.TILE_SIDE)
            )
            return
        self.add_entity(entity((col, row), image, properties))

    def load_entities_from_room(self) -> None:
        for layer in shared.room_map.layers:
            for x, y, image in layer.tiles():
                gid = layer.data[y][x]
                properties = shared.room_map.get_tile_properties_by_gid(gid)
                if properties is None:
                    entity_id = None
                else:
                    entity_id = properties["type"]
                self.place_entity(
                    y, x, entity_id=entity_id, image=image, properties=properties
                )

        Grid.LOADED_BACKGROUNDS[shared.room_id] = self.background.copy()

    def align_player_pos(self) -> None:
        for entity in shared.entities:
            if isinstance(entity, Door) and entity.door_direction == shared.next_door:
                player_index = shared.entities.index(shared.player)
                shared.entities[player_index] = Player(
                    entity.cell,
                    shared.player.image,
                    shared.player.properties,
                )

                return

    def draw_grid(self) -> None:
        for row in range(shared.rows + 1):
            start = 0, row * shared.TILE_SIDE
            end = shared.WIN_WIDTH, row * shared.TILE_SIDE
            pygame.draw.line(shared.screen, Grid.LINE_COLOR, start, end)

        for col in range(shared.cols + 1):
            start = col * shared.TILE_SIDE, 0
            end = col * shared.TILE_SIDE, shared.WIN_HEIGHT
            pygame.draw.line(shared.screen, Grid.LINE_COLOR, start, end)

    def filter_entities(self) -> tuple[list[Entity], list[Entity]]:
        background_entities: list[Entity] = []
        foreground_entities: list[Entity] = []

        for entity in shared.entities:
            if entity is shared.player:
                continue
            if entity.movement_type == MovementType.FOREGROUND:
                foreground_entities.append(entity)
            else:
                background_entities.append(entity)

            # this just forces holes to be the first things drawn
            background_entities.sort(key=lambda e: int(not isinstance(e, Hole)))
            background_entities.sort(key=lambda e: int(not isinstance(e, MagicHole)))

        return background_entities, foreground_entities

    def draw(self) -> None:
        # self.draw_grid()
        shared.screen.blit(self.background, get_relative_pos(pygame.Vector2()))

        bg_entities, fg_entities = self.filter_entities()
        for entity in bg_entities:
            entity.draw()
        shared.player.draw()
        for entity in fg_entities:
            entity.draw()
