import abc

import pygame

from . import shared
from .enums import MovementType
from .gameobject import GameObject


class Entity(GameObject):
    def __init__(self, cell, movement_type, image) -> None:
        self.cell = cell
        self.movement_type = movement_type

        self.cell = pygame.Vector2(cell)
        self.pos = self.cell * shared.TILE_SIDE
        self.rect = image.get_rect(topleft=self.pos)
        self.desired_cell = self.cell.copy()
        self.desired_pos = self.pos.copy()
        self._direction = (0, 0)
        self.moving = False
        super().__init__(self.pos, is_visible=True, is_interactable=True, image=image)

    @property
    def direction(self) -> tuple[int, int]:
        return self._direction

    @direction.setter
    def direction(self, new_direction):
        self._direction = new_direction
        self.desired_cell = self.cell + self.direction
        self.desired_pos = self.desired_cell * shared.TILE_SIDE
        self.moving = True

    def move(self):
        self.pos.move_towards_ip(self.desired_pos, shared.ENTITY_SPEED * shared.dt)
        self.rect.topleft = self.pos

    def transfer_cell(self):
        if self.pos == self.desired_pos:
            self.cell = self.desired_cell.copy()
            self.moving = False
        else:
            self.moving = True

    def update(self):
        self.move()
        self.transfer_cell()


class Wall(Entity):
    def __init__(self, cell: tuple[int, int]) -> None:
        image = pygame.Surface(shared.TILE_SIZE)
        image.fill("brown")
        super().__init__(cell, MovementType.STATIC, image)


class Player(Entity):
    CONTROLS = {
        # Arrow keys
        pygame.K_RIGHT: (1, 0),
        pygame.K_LEFT: (-1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        # WASD
        pygame.K_d: (1, 0),
        pygame.K_a: (-1, 0),
        pygame.K_w: (0, -1),
        pygame.K_s: (0, 1),
    }

    def __init__(self, cell: tuple[int, int]) -> None:
        image = pygame.Surface(shared.TILE_SIZE)
        image.fill("red")
        super().__init__(cell, MovementType.CONTROLLED, image)

    def scan_controls(self):
        if self.moving:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key in Player.CONTROLS:
                self.direction = Player.CONTROLS[event.key]

        for control in Player.CONTROLS:
            if shared.keys[control]:
                self.direction = Player.CONTROLS[control]

    def scan_surroundings(self):
        for entity in shared.entities:
            if entity.cell == self.cell:
                continue
            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.PUSHED
                and isinstance(entity, Stone)
            ):
                entity.direction = self.direction

            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.STATIC
            ):
                self.direction = (0, 0)

    def update(self):
        self.scan_controls()
        super().update()
        self.scan_surroundings()


class Stone(Entity):
    def __init__(self, cell) -> None:
        image = pygame.Surface(shared.TILE_SIZE)
        image.fill((50, 50, 50))
        super().__init__(cell, MovementType.PUSHED, image)

    def scan_surroundings(self):
        for entity in shared.entities:
            if entity.cell == self.cell:
                continue
            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.PUSHED
            ):
                entity.direction = self.direction

            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.STATIC
            ):
                self.direction = (0, 0)

    def update(self):
        super().update()
        self.scan_surroundings()
