import itertools
import typing as t

import pygame

from . import shared
from .anim import Animation, get_frames
from .bloom import Bloom
from .common import render_at
from .enums import DoorDirection, MovementType, StoneSymbol
from .gameobject import GameObject, get_relative_pos
from .gamestate import GameStateManager


class Entity(GameObject):
    def __init__(self, cell, movement_type, image) -> None:
        self.cell = pygame.Vector2(cell)
        self.movement_type = movement_type

        self.pos = self.cell * shared.TILE_SIDE
        self.rect: pygame.Rect = image.get_rect(topleft=self.pos)
        self.desired_cell = self.cell.copy()
        self.desired_pos = self.pos.copy()
        self._direction = (0, 0)
        self.moving = False
        self.is_alive = True
        super().__init__(self.pos, is_visible=True, is_interactable=True, image=image)

    @property
    def direction(self) -> tuple[int, int]:
        return self._direction

    @direction.setter
    def direction(self, new_direction) -> None:
        self._direction = new_direction
        self.desired_cell = self.cell + self.direction
        self.desired_pos = self.desired_cell * shared.TILE_SIDE
        self.moving = True

    def request_direction(self, new_direction) -> bool:
        return True

    def get_surrounding_entities(self) -> t.Iterator[t.Self]:
        for row in (-1, 0, 1):
            for col in (-1, 0, 1):
                entity_cell = self.cell + (row, col)
                if (
                    entity_cell.x > shared.room_map.width
                    or entity_cell.y > shared.room_map.height
                ):
                    continue
                try:
                    yield shared.entities[shared.cells.index(entity_cell)]
                except ValueError:
                    continue

    def get_cell_diff(self, other_cell):
        return abs(self.cell[0] - other_cell[0]), abs(self.cell[1] - other_cell[1])

    def move(self) -> None:
        if self.desired_pos != self.pos:
            shared.update_graph = True
        self.pos.move_towards_ip(self.desired_pos, shared.ENTITY_SPEED * shared.dt)
        self.rect.topleft = self.pos

    def transfer_cell(self) -> None:
        if self.pos == self.desired_pos:
            self.cell = self.desired_cell.copy()
            self.moving = False
        else:
            self.moving = True

    def update(self) -> None:
        self.move()
        self.transfer_cell()


class MagicHole(Entity):
    FRAMES = get_frames(shared.ART_PATH / "magic-blocks.png", (64, 64))
    BLOCK_IMAGES = {char: image for char, image in zip("OPEN", FRAMES[4:])}

    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.HOLE, image.copy())

        self.character = properties["character"]
        self.filled = False


class MagicBlock(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.PUSHED, image.copy())
        self.char_cycle = itertools.cycle("OPEN")
        self.character = self.properties["character"]
        char = next(self.char_cycle)
        while char != self.character:
            char = next(self.char_cycle)
        self.falling = False
        self.anims = None

    def check_placed(self):
        for entity in shared.entities:
            if (
                entity.cell == self.cell
                and isinstance(entity, MagicHole)
                and entity.character == self.character
            ):
                return True

        return False

    def transfer_cell(self) -> None:
        if not self.moving:
            return
        if self.pos == self.desired_pos:
            self.cell = self.desired_cell.copy()
            self.moving = False

            if self.check_placed():
                return
            self.character = next(self.char_cycle)
            self.image = MagicHole.BLOCK_IMAGES[self.character].copy()
        else:
            self.moving = True

    def scan_surroundings(self) -> None:
        if self.falling:
            self.direction = (0, 0)
            return

        for entity in shared.entities:
            if entity.cell == self.desired_cell:
                if isinstance(entity, MagicHole) and self.character != entity.character:
                    self.direction = (0, 0)
                    return

            if entity.cell == self.cell:
                if isinstance(entity, MagicHole) and self.character == entity.character:
                    shared.check_solve = True
                    self.falling = True
                else:
                    continue

            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.PUSHED
            ):
                if entity.request_direction(self.direction):
                    entity.direction = self.direction
                else:
                    self.direction = (0, 0)

            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.STATIC
            ):
                self.direction = (0, 0)
                return

    def request_direction(self, new_direction) -> bool:
        desired_cell = self.cell + new_direction

        for entity in shared.entities:
            if entity.cell == desired_cell:
                if isinstance(entity, MagicHole) and self.character != entity.character:
                    return False
                elif entity.movement_type == MovementType.STATIC:
                    return False
                elif entity.movement_type == MovementType.PUSHED:
                    if entity.falling:
                        return False
                    return entity.request_direction(new_direction)

        return True

    def update(self) -> None:
        super().update()
        self.scan_surroundings()
        if self.falling:
            try:
                self.animate_fall()
            except StopIteration:
                self.falling = False
                self.movement_type = MovementType.STATIC

                for entity in shared.entities:
                    if (
                        entity.rect.colliderect(self.rect)
                        and entity.movement_type == MovementType.HOLE
                    ):
                        entity.movement_type = MovementType.WALKABLE
                        entity.filled = True
                shared.check_solve = True

    def set_falling(self, toggle: bool) -> None:
        self.falling = toggle

    def animate_fall(self) -> None:
        if self.anims is None:
            cd = 0.2
            frames: list[pygame.Surface] = [self.image.copy()]

            fall_distance = 0
            while fall_distance < self.image.get_height() // 4:
                fall_distance += 1
                self.image.scroll(0, 1)
                pygame.draw.rect(
                    self.image,
                    (0, 0, 0, 0),
                    pygame.Rect(0, 0, self.image.get_width(), fall_distance),
                )
                frames.append(self.image.copy())

            self.anims = Animation(frames, cd, False)
            self.image.scroll(0, -self.image.get_height() // 4)

        self.anims.update()
        self.image = self.anims.current_frame


class Torch(Entity):
    FRAMES = get_frames(shared.ART_PATH / "torch.png", (64, 64))

    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.STATIC, image)

        self.lit = False
        self.near = False
        self.clicked = False
        self.original_image = self.image.copy()
        self.anim = Animation(Torch.FRAMES, 0.3)
        self.bloom = Bloom(
            (500, 500),
            0.6,
            40,
            layers=[(255, 255, 100)],
        )

    def check_clicked(self):
        for event in shared.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                relative_rect = self.rect.copy()
                relative_rect.topleft = get_relative_pos(relative_rect.topleft)

                if relative_rect.collidepoint(shared.mouse_pos):
                    self.clicked = True
                    if self.near:
                        shared.check_solve = True

    def check_near(self):
        self.near = self.get_cell_diff(shared.player.cell) >= (0, 0)

    def check_lit(self):
        self.lit = self.near and self.clicked

    def on_lit(self):
        if self.lit:
            self.anim.update()
            self.bloom.update(self.rect.center)
            self.image = self.anim.current_frame.copy()
        else:
            self.image = self.original_image.copy()

    def update(self):
        super().update()
        self.check_near()
        self.check_clicked()
        self.check_lit()
        self.on_lit()

    def draw(self) -> None:
        super().draw()
        if self.lit:
            self.bloom.draw()


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

        # making temporary comparisons to allow for doors that are taller
        # but also the placeholder single doors
        if self.cell[1] <= 1:
            self.door_direction = DoorDirection.NORTH
            self.room_delta = -3
        elif self.cell[0] >= shared.room_map.width - 2:
            self.door_direction = DoorDirection.EAST
            self.room_delta = 1
        elif self.cell[0] <= 1:
            self.door_direction = DoorDirection.WEST
            self.room_delta = -1
        elif self.cell[1] >= shared.room_map.height - 2:
            self.door_direction = DoorDirection.SOUTH
            self.room_delta = 3
        self.next_door = Door.DOOR_CONNECTION.get(self.door_direction)
        if shared.room_id == 1:
            self.locked = True
        else:
            self.locked = self.door_direction != shared.next_door

    def draw(self) -> None:
        return


class Wall(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.STATIC, image)

    def draw(self) -> None:
        return


class Pillar(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.STATIC, image)


class Foreground(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.FOREGROUND, image)


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
        self.bloom = Bloom((500, 500), wave_speed=2, expansion_factor=35)
        self.img_rect = self.image.get_rect()

    def init_anim(self) -> None:
        frames = get_frames(shared.ART_PATH / "player-128.png", (64, 128))

        for index, frame in enumerate(frames):
            base = pygame.Surface(
                (shared.TILE_SIDE, 2 * shared.TILE_SIDE), pygame.SRCALPHA
            )
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

    def scan_controls(self) -> None:
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

    def travel_to_next_room(self, entity: Entity):
        shared.entities_in_room[shared.room_id] = shared.entities.copy()
        shared.room_id += entity.room_delta
        shared.next_door = entity.next_door
        GameStateManager().set_state("PlayState")

    def scan_surroundings(self) -> None:
        for entity in self.get_surrounding_entities():
            if entity.cell == self.cell:
                continue
            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.PUSHED
            ):
                if entity.request_direction(self.direction):
                    entity.direction = self.direction
                else:
                    self.direction = (0, 0)

            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.STATIC
            ):
                if isinstance(entity, Door) and not entity.locked:
                    self.travel_to_next_room(entity)
                self.direction = (0, 0)
            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.HOLE
            ):
                self.direction = (0, 0)

    def update_anim(self) -> None:
        if not self.moving or self.direction == (0, 0):
            self.image = self.anims[self.last_direction].indexable_frames[0]
            return
        self.anims[self.direction].update()
        self.image = self.anims[self.direction].current_frame

    def update(self) -> None:
        self.scan_controls()
        super().update()
        self.img_rect.center = self.rect.center
        self.bloom.update(self.img_rect.center)
        self.scan_surroundings()
        self.update_anim()

    def draw(self) -> None:
        if self.is_visible and self.image is not None:
            shared.screen.blit(
                self.image, self.image.get_rect(midleft=get_relative_pos(self.pos))
            )
        self.bloom.draw()


class Stone(Entity):
    SYMBOL_MAP = {
        "teacup": StoneSymbol.TEACUP,
        "switzerland": StoneSymbol.SWITZERLAND,
        "pirate": StoneSymbol.PIRATE,
        "wales": StoneSymbol.WALES,
        "ireland": StoneSymbol.IRELAND,
    }

    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.PUSHED, image.copy())
        self.falling = False
        self.anims = None
        self.symbol = Stone.SYMBOL_MAP.get(self.properties["symbol"])

    def scan_surroundings(self) -> None:
        if self.falling:
            self.direction = (0, 0)
            return

        for entity in shared.entities:
            if entity.cell == self.desired_cell:
                if (
                    entity.movement_type == MovementType.HOLE
                    and isinstance(entity, MagicHole)
                    and self.symbol != entity.symbol
                ):
                    self.direction = (0, 0)
                    return

            if entity.cell == self.cell:
                if (
                    entity.movement_type == MovementType.HOLE
                    and self.symbol == entity.symbol
                ):
                    shared.check_solve = True
                    self.falling = True
                else:
                    continue

            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.PUSHED
            ):
                if entity.request_direction(self.direction):
                    entity.direction = self.direction
                else:
                    self.direction = (0, 0)

            if (
                entity.cell == self.desired_cell
                and entity.movement_type == MovementType.STATIC
            ):
                self.direction = (0, 0)
                return

    def request_direction(self, new_direction) -> bool:
        desired_cell = self.cell + new_direction

        for entity in shared.entities:
            if entity.cell == desired_cell:
                if (
                    entity.movement_type == MovementType.HOLE
                    and self.symbol != entity.symbol
                ):
                    return False
                elif entity.movement_type == MovementType.STATIC:
                    return False
                elif entity.movement_type == MovementType.PUSHED:
                    if entity.falling:
                        return False
                    return entity.request_direction(new_direction)

        return True

    def update(self) -> None:
        super().update()
        self.scan_surroundings()
        if self.falling:
            try:
                self.animate_fall()
            except StopIteration:
                self.falling = False
                self.movement_type = MovementType.WALKABLE
                for entity in shared.entities:
                    if (
                        entity.rect.colliderect(self.rect)
                        and entity.movement_type == MovementType.HOLE
                    ):
                        entity.movement_type = MovementType.WALKABLE
                        entity.filled = True
                shared.check_solve = True

    def animate_fall(self) -> None:
        if self.anims is None:
            cd = 0.2
            frames: list[pygame.Surface] = [self.image.copy()]

            fall_distance = 0
            while fall_distance < self.image.get_height() // 4:
                fall_distance += 1
                self.image.scroll(0, 1)
                pygame.draw.rect(
                    self.image,
                    (0, 0, 0, 0),
                    pygame.Rect(0, 0, self.image.get_width(), fall_distance),
                )
                frames.append(self.image.copy())

            self.anims = Animation(frames, cd, False)
            self.image.scroll(0, -self.image.get_height() // 4)

        self.anims.update()
        self.image = self.anims.current_frame


class Hole(Entity):
    def __init__(
        self,
        cell: tuple[int, int],
        image: pygame.Surface,
        properties: dict,
    ) -> None:
        self.properties = properties
        super().__init__(cell, MovementType.HOLE, image)
        self.symbol = Stone.SYMBOL_MAP.get(self.properties["symbol"])
        self.filled = False
