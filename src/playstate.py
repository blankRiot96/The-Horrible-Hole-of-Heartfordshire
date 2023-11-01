import random

import pygame

import pytmx

from . import shared
from .common import Time
from .entities import Door, Monster
from .gamestate import GameState
from .grid import Grid


def load_room():
    """Loads room from room ID"""
    shared.room_map = pytmx.load_pygame(shared.ROOMS_PATH / f"{shared.room_id}.tmx")  # type: ignore
    shared.rows = shared.room_map.height
    shared.cols = shared.room_map.width


class PlayState(GameState):
    def __init__(self) -> None:
        super().__init__("PlayState")
        load_room()
        self.grid = Grid()
        self.grid.load_entities_from_room()
        shared.camera_pos = pygame.Vector2(shared.player.rect.center)
        self.cam_speed = shared.ENTITY_SPEED * 0.65
        shared.overlay = pygame.Surface(shared.WIN_SIZE)
        self.monster_timer = Time(shared.monster_move_time)
        self.monster_spawned = True

    def handle_events(self) -> None:
        ...

    def handle_camera(self) -> None:
        shared.camera_pos.move_towards_ip(
            shared.player.rect.center, self.cam_speed * shared.dt
        )
        self.cam_speed = (shared.ENTITY_SPEED * 0.65) * (
            shared.camera_pos.distance_to(shared.player.rect.center) / 75
        )

    def check_monster_move(self) -> None:
        if not self.monster_timer.tick():
            return

        will_change = random.random() < shared.monster_move_chance
        if will_change:
            diffs = [-1, 1, -3, 3]
            possible_rooms = []
            for diff in diffs:
                test_room = shared.monster_room + diff
                if abs(diff) == 3:
                    if 0 < test_room < 10:
                        possible_rooms.append(test_room)
                else:
                    if (test_room - 1) // 3 == (shared.monster_room - 1) // 3:
                        possible_rooms.append(test_room)

            shared.monster_last_room = shared.monster_room
            shared.monster_room = random.choice(possible_rooms)
            print(f"Moved from {shared.monster_last_room} to {shared.monster_room}")

    def spawn_monster(self) -> None:
        self.monster_spawned = True
        monster_index = shared.entities.index(shared.monster)
        doors = [entity for entity in shared.entities if isinstance(entity, Door)]
        if shared.monster_room - shared.monster_last_room == 1:
            # right door
            door = sorted(doors, key=lambda entity: entity.cell.x)[-1]
        elif shared.monster_room - shared.monster_last_room == -1:
            # left door
            door = sorted(doors, key=lambda entity: entity.cell.x)[0]
        elif shared.monster_room - shared.monster_last_room == 3:
            # bottom door
            door = sorted(doors, key=lambda entity: entity.cell.y)[-1]
        else:
            # top door
            door = sorted(doors, key=lambda entity: entity.cell.y)[0]
        shared.entities[monster_index] = Monster(
            door.cell, shared.monster.image, shared.monster.properties
        )
        shared.monster = shared.entities[monster_index]

    def despawn_monster(self) -> None:
        self.monster_spawned = False
        monster_index = shared.entities.index(shared.monster)
        shared.entities[monster_index] = Monster(
            (-100, -100), shared.monster.image, shared.monster.properties
        )
        shared.monster = shared.entities[monster_index]

    def update(self) -> None:
        self.grid.update()
        self.handle_camera()
        if shared.monster_room != shared.room_id:
            if self.monster_spawned:
                self.despawn_monster()

            self.check_monster_move()
        elif not self.monster_spawned:
            self.spawn_monster()

    def draw(self) -> None:
        shared.overlay.fill("black")
        self.grid.draw()
        shared.screen.blit(shared.overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
