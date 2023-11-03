import pygame

from . import shared
from .entities import Door, Hole, MagicHole, Torch
from .enums import DoorDirection
from .gameobject import get_relative_pos


class Lock:
    LOCK_IMAGE = pygame.image.load(shared.ART_PATH / "lock.png").convert_alpha()
    LOCK_IMAGE = pygame.transform.scale(LOCK_IMAGE, (32, 32))

    def __init__(
        self, center_pos: pygame.Vector2, door_direction: DoorDirection
    ) -> None:
        self.pos: pygame.Vector2 = center_pos.copy()
        self.door_direction = door_direction
        self.set_image_to_door()
        self.rect = self.image.get_rect(center=self.pos)

    def flip_image_right(self, x):
        if x > 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif x < 0:
            self.image = pygame.transform.rotate(self.image, -90)

    def set_image_to_door(self):
        self.image = Lock.LOCK_IMAGE.copy()
        x, y = self.door_direction.value
        self.image = pygame.transform.flip(self.image, False, y < 0)
        self.flip_image_right(x)
        self.pos.x -= x * 48
        self.pos.y -= y * 48

    def draw(self):
        shared.screen.blit(self.image, get_relative_pos(self.rect.topleft))


class PuzzleManager:
    """Handles opening doors and solving puzzles."""

    SOLVED_ROOMS = {room_no: False for room_no in range(1, 10)}

    def __init__(self) -> None:
        self.room_solve_checkers = {
            1: self.check_stone_hole_solved,
            2: self.check_magic_solved,
            4: self.check_combination_lock_solved,
        }
        if shared.reset:
            PuzzleManager.SOLVED_ROOMS = {room_no: False for room_no in range(1, 10)}
        self.place_locks()

    def place_locks(self):
        self.locks: list[Lock] = []
        for entity in shared.entities:
            if isinstance(entity, Door):
                if shared.room_id != 1 and shared.next_door == entity.door_direction:
                    continue
                lock = Lock(pygame.Vector2(entity.rect.center), entity.door_direction)
                self.locks.append(lock)

    def on_solve(self):
        for entity in shared.entities:
            if isinstance(entity, Door):
                entity.locked = False

    def check_stone_hole_solved(self):
        for entity in shared.entities:
            if isinstance(entity, Hole) and not entity.filled:
                PuzzleManager.SOLVED_ROOMS[shared.room_id] = False
                return

        PuzzleManager.SOLVED_ROOMS[shared.room_id] = True
        self.on_solve()

    def check_magic_solved(self):
        for entity in shared.entities:
            if isinstance(entity, MagicHole) and not entity.filled:
                PuzzleManager.SOLVED_ROOMS[shared.room_id] = False
                return

        PuzzleManager.SOLVED_ROOMS[shared.room_id] = True
        self.on_solve()

    def check_combination_lock_solved(self):
        """
        The riddle goes like this:
        'This creature dwelves in the sea.. it has stretchy arms and its name starts
        with the word in room 8.. light the first and nth torch where n is the number
        of arms this sea creature has.'

        So basically check if the first and 8th torch are lit
        """
        torches = [entity for entity in shared.entities if isinstance(entity, Torch)]

        if torches[0].lit and torches[7].lit:
            PuzzleManager.SOLVED_ROOMS[shared.room_id] = True
            self.on_solve()
            return

        PuzzleManager.SOLVED_ROOMS[shared.room_id] = False

    def update(self):
        if not shared.check_solve:
            return
        self.room_solve_checkers[shared.room_id]()
        shared.check_solve = False

    def draw(self):
        if PuzzleManager.SOLVED_ROOMS[shared.room_id]:
            return

        for lock in self.locks:
            lock.draw()
