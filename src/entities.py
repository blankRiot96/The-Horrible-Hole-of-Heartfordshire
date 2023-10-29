import pygame

from . import shared
from .anim import Animation, get_frames
from .common import render_at
from .enums import DoorDirection, MovementType
from .gameobject import GameObject
from .gamestate import GameStateManager


class Entity(GameObject):
    def __init__(self, cell, movement_type, image) -> None:
        self.cell = pygame.Vector2(cell)
        self.movement_type = movement_type

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


class Torch(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.STATIC, image)


class Door(Entity):
    DOOR_CONNECTION = {
        DoorDirection.SOUTH: DoorDirection.NORTH,
        DoorDirection.NORTH: DoorDirection.SOUTH,
        DoorDirection.WEST: DoorDirection.EAST,
        DoorDirection.EAST: DoorDirection.WEST,
    }

    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.STATIC, image)

        if self.cell[1] == 0:
            self.door_direction = DoorDirection.NORTH
            self.room_delta = -3
        elif self.cell[0] == shared.room_map.width - 1:
            self.door_direction = DoorDirection.EAST
            self.room_delta = 1
        elif self.cell[0] == 0:
            self.door_direction = DoorDirection.WEST
            self.room_delta = -1
        elif self.cell[1] == shared.room_map.height - 1:
            self.door_direction = DoorDirection.SOUTH
            self.room_delta = 3
        self.next_door = Door.DOOR_CONNECTION.get(self.door_direction)


class Wall(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
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

    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.CONTROLLED, image)
        shared.player = self
        self.direction = shared.next_door.value
        self.init_anim()

    def init_anim(self):
        frames = get_frames(shared.ART_PATH / "player-64.png", (32, 64))

        for index, frame in enumerate(frames):
            base = pygame.Surface((shared.TILE_SIDE, shared.TILE_SIDE), pygame.SRCALPHA)
            render_at(base, frame, "center")
            frames[index] = base

        south_frames = frames[:4]
        east_frames = frames[4:8]
        west_frames = [
            pygame.transform.flip(frame, True, False) for frame in east_frames
        ]
        north_frames = frames[8:12]
        anim_cd = 0.2
        self.anims = {
            (0, -1): Animation(north_frames, anim_cd),
            (1, 0): Animation(east_frames, anim_cd),
            (-1, 0): Animation(west_frames, anim_cd),
            (0, 1): Animation(south_frames, anim_cd),
        }
        self.last_direction = (0, 1)

    def scan_controls(self):
        if self.moving:
            return

        for event in shared.events:
            if event.type == pygame.KEYDOWN and event.key in Player.CONTROLS:
                self.direction = Player.CONTROLS[event.key]

        for control in Player.CONTROLS:
            if shared.keys[control]:
                self.direction = Player.CONTROLS[control]

        if self.direction == (0, 0):
            return
        self.last_direction = self.direction

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
                if isinstance(entity, Door):
                    shared.room_id += entity.room_delta
                    shared.next_door = entity.next_door
                    GameStateManager().set_state("PlayState")

                self.direction = (0, 0)

    def update_anim(self):
        if not self.moving or self.direction == (0, 0):
            self.image = self.anims[self.last_direction].indexable_frames[0]
            return
        self.anims[self.direction].update()
        self.image = self.anims[self.direction].current_frame

    def update(self):
        self.scan_controls()
        super().update()
        self.scan_surroundings()
        self.update_anim()


class Stone(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
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
