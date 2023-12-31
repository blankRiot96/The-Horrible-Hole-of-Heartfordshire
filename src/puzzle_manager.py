import pygame

from . import shared
from .common import get_path
from .entities import Door, Hole, MagicHole, Torch
from .enums import DoorDirection
from .gameobject import get_relative_pos


class Lock:
    LOCK_IMAGE = pygame.image.load(get_path("assets/art/lock.png")).convert_alpha()
    LOCK_IMAGE = pygame.transform.scale(LOCK_IMAGE, (32, 32))

    GOLDEN_IMAGE = pygame.image.load(
        get_path("assets/art/golden-lock.png")
    ).convert_alpha()
    GOLDEN_IMAGE = pygame.transform.scale(GOLDEN_IMAGE, (32, 32))

    def __init__(
        self, center_pos: pygame.Vector2, door_direction: DoorDirection
    ) -> None:
        self.pos: pygame.Vector2 = center_pos.copy()
        self.door_direction = door_direction
        self.golden = shared.room_id == 8 and self.door_direction == DoorDirection.SOUTH
        self.set_image_to_door()
        self.rect = self.image.get_rect(center=self.pos)

    def flip_image_right(self, x):
        if x > 0:
            self.image = pygame.transform.rotate(self.image, 90)
        elif x < 0:
            self.image = pygame.transform.rotate(self.image, -90)

    def set_image_to_door(self):
        if self.golden:
            self.image = Lock.GOLDEN_IMAGE.copy()
        else:
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

    SOLVED_ROOMS = {
        room_no: True if room_no in shared.MAZE_ROOMS else False
        for room_no in range(1, 10)
    }

    def __init__(self) -> None:
        self.room_solve_checkers = {
            1: self.check_stone_hole_solved,
            2: self.check_combination_lock_solved_rm_2,
            4: self.check_combination_lock_solved_rm_4,
            5: self.check_combo_room_solved,
            6: self.check_stone_hole_solved,
            8: self.check_magic_solved,
            9: self.check_complex_lock_solved,
        }
        if shared.reset:
            PuzzleManager.SOLVED_ROOMS = {
                room_no: True if room_no in shared.MAZE_ROOMS else False
                for room_no in range(1, 10)
            }

        if shared.room_id in shared.MAZE_ROOMS:
            self.on_solve()
        self.place_locks()
        shared.win = all(PuzzleManager.SOLVED_ROOMS.values())

        if shared.room_id == 8 and shared.win:
            self.on_solve()

    def place_locks(self):
        self.locks: list[Lock] = []
        for entity in shared.entities:
            if isinstance(entity, Door):
                if shared.room_id != 1 and shared.next_door == entity.door_direction:
                    continue
                lock = Lock(pygame.Vector2(entity.rect.center), entity.door_direction)
                self.locks.append(lock)

    def on_win(self, entity: Door):
        if (
            shared.room_id == 8
            and entity.door_direction == DoorDirection.SOUTH
            and not shared.win
        ):
            entity.locked = True

    def on_solve(self):
        for entity in shared.entities:
            if isinstance(entity, Door):
                entity.locked = False
                self.on_win(entity)

    def check_combo_room_solved(self):
        torches = []

        for entity in shared.entities:
            if isinstance(entity, Torch):
                torches.append(entity)
                continue
            if isinstance(entity, Hole) and not entity.filled:
                PuzzleManager.SOLVED_ROOMS[shared.room_id] = False
                return

        if not all(torch.lit for torch in torches):
            PuzzleManager.SOLVED_ROOMS[shared.room_id] = False
            return

        PuzzleManager.SOLVED_ROOMS[shared.room_id] = True
        self.on_solve()

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

    def check_combination_lock_solved_rm_2(self):
        """
        Light the way
        """
        torches = [entity for entity in shared.entities if isinstance(entity, Torch)]

        if all(torch.lit for torch in torches):
            PuzzleManager.SOLVED_ROOMS[shared.room_id] = True
            self.on_solve()
            return

        PuzzleManager.SOLVED_ROOMS[shared.room_id] = False

    def check_combination_lock_solved_rm_4(self):
        """
        The riddle goes like this:
        'This creature dwelves in the sea.. it has stretchy arms and its name starts
        with the word in room 8.. light the first and nth torch where n is the number
        of arms this sea creature has.'

        So basically check if the first and 8th torch are lit
        """
        torches = [entity for entity in shared.entities if isinstance(entity, Torch)]

        if (
            torches[0].lit
            and torches[7].lit
            and all(not torch.lit for torch in torches[1:7])
        ):
            PuzzleManager.SOLVED_ROOMS[shared.room_id] = True
            self.on_solve()
            return

        PuzzleManager.SOLVED_ROOMS[shared.room_id] = False

    def check_complex_lock_solved(self):
        torches = [entity for entity in shared.entities if isinstance(entity, Torch)]

        if (
            torches[0].lit
            and torches[5].lit
            and all(not torch.lit for i, torch in enumerate(torches) if i not in (0, 5))
        ):
            PuzzleManager.SOLVED_ROOMS[shared.room_id] = True
            self.on_solve()
            return

        PuzzleManager.SOLVED_ROOMS[shared.room_id] = False

    def update(self):
        if (
            shared.win
            or not shared.check_solve
            or PuzzleManager.SOLVED_ROOMS[shared.room_id]
        ):
            return
        self.room_solve_checkers[shared.room_id]()
        shared.check_solve = False

    def draw(self):
        if PuzzleManager.SOLVED_ROOMS[shared.room_id] and shared.room_id != 8:
            return

        for lock in self.locks:
            if (
                shared.room_id == 8
                and PuzzleManager.SOLVED_ROOMS[shared.room_id]
                and not lock.golden
            ):
                continue

            if shared.win:
                continue
            lock.draw()
