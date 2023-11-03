import random

import pygame

from . import shared
from .anim import Animation, get_frames
from .asset_loader import Loader
from .common import Time, get_path, render_at
from .entities import Door
from .enums import DoorDirection
from .gameobject import GameObject
from .gamestate import GameStateManager
from .graph import Graph


class Monster(GameObject):
    def __init__(self) -> None:
        self.init_anim()
        super().__init__(
            pos=pygame.Vector2(),
            is_visible=True,
            is_interactable=True,
            image=pygame.Surface(shared.TILE_SIZE),
        )
        self.chasing = False
        if shared.monster_audio is None:
            shared.monster_audio = Loader().get_sound(
                get_path("assets/audio/hhhcreeps.ogg")
            )

        self.cooldown_timer = Time(60)
        self.on_cooldown = False

    def init_anim(self) -> None:
        frames = get_frames(shared.ART_PATH / "monster-64.png", (64, 64))

        for index, frame in enumerate(frames):
            base = pygame.Surface((shared.TILE_SIDE, shared.TILE_SIDE), pygame.SRCALPHA)
            render_at(base, frame, "center")
            frames[index] = base

        number_frames = 7
        south_frames = frames[:number_frames]
        south_frames += south_frames[-2:0:-1]
        east_frames = frames[number_frames : 2 * number_frames]
        east_frames += east_frames[-2:0:-1]
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
        self.last_pos = pygame.Vector2()

    def align_pos_with_door(self, door_direction: DoorDirection):
        for entity in shared.entities:
            if isinstance(entity, Door) and entity.door_direction == door_direction:
                self.pos = entity.pos.copy()
                self.new_pos = self.pos.copy()
                return

    def get_delta_direction(self):
        x, y = self.pos - self.last_pos
        if x != 0:
            return (1 if x > 0 else -1, 0)
        if y != 0:
            return (0, 1 if y > 0 else -1)

        return (0, 1)

    def pathfind_to_player(self) -> None:
        """
        Just moves toward the player in a straight line for now. When implementing
        actual pathfinding you can use `shared.entities` which contain the absolute pos
        as `Entity.pos` and their rect as `Entity.rect` which you may require.
        """
        if (
            shared.monster_audio is not None
            and not shared.monster_audio.get_num_channels()
        ):
            shared.monster_audio.play(-1)
        self.chasing = True

        if shared.update_graph:
            shared.update_graph = False
            shared.graph = Graph()
            shared.graph.create_graph()

            monster_cell = int(self.pos.y / shared.TILE_SIDE), int(
                self.pos.x / shared.TILE_SIDE
            )
            player_cell = int(shared.player.cell.y), int(shared.player.cell.x)
            self.path = shared.graph.search(monster_cell, player_cell)
            if self.pos == self.new_pos:
                self.new_pos = (
                    pygame.Vector2(self.path.popleft()) * shared.TILE_SIDE
                ).yx

        if self.path:
            if self.pos == self.new_pos:
                self.new_pos = (
                    pygame.Vector2(self.path.popleft()) * shared.TILE_SIDE
                ).yx
            self.pos.move_towards_ip(
                self.new_pos, shared.ENTITY_SPEED * 0.3 * shared.dt
            )

    def update_anim(self) -> None:
        anim = self.anims.get(self.get_delta_direction())
        anim.update()
        self.image = anim.current_frame
        self.last_pos = self.pos.copy()

    def update(self) -> None:
        self.cooldown_timer.reset()
        self.on_cooldown = True
        print("on cooldown")
        self.update_anim()
        self.pathfind_to_player()
        if self.image.get_rect(topleft=self.pos).colliderect(
            shared.player.image.get_rect(midleft=shared.player.pos)
        ):
            GameStateManager().set_state("DeathScreen")


class MonsterManager:
    PLAYER_CHASE_DISTANCE = 200
    CHASE_INTERVAL = 1.0

    def __init__(self) -> None:
        self.room = 9
        self.last_room = -1
        self.move_chance = 0.3
        self.move_time = 15  # seconds
        self.timer = Time(self.move_time)
        self.create_monster()

    def create_monster(self):
        self.must_align = False
        self.align_timer = Time(
            MonsterManager.CHASE_INTERVAL
        )  # Wait 1 second before entering the next room
        # with the player

        if not hasattr(shared, "monster"):
            shared.monster = Monster()

        # If the monster was still chasing the player while
        # he moved into the next room, chase him into the next room as well
        if (
            shared.monster.chasing
            and shared.monster.pos.distance_to(shared.player.pos)
            < MonsterManager.PLAYER_CHASE_DISTANCE
        ):
            self.must_align = True

    def change_room(self):
        if not self.timer.tick() or random.random() > self.move_chance:
            shared.monster.chasing = False
            return

        # Maps the diff to the entrance direction
        diffs = {
            -1: DoorDirection.EAST,
            1: DoorDirection.WEST,
            -3: DoorDirection.SOUTH,
            3: DoorDirection.NORTH,
        }
        possible_rooms = []

        # store the possible diffs as well, which will append the diff mapping
        # to the possible room chosen. this way we can get the diff through which the
        # possible room was chosen, with which we can assign the door from which
        # the monster enters
        possible_diffs = []
        for diff in diffs:
            test_room = self.room + diff
            if abs(diff) == 3:
                if 0 < test_room < 10:
                    possible_rooms.append(test_room)
                    possible_diffs.append(diff)
            else:
                if (test_room - 1) // 3 == (self.room - 1) // 3:
                    possible_rooms.append(test_room)
                    possible_diffs.append(diff)

        if shared.monster.on_cooldown:
            if shared.monster.cooldown_timer.tick():
                shared.monster.on_cooldown = False
            elif shared.room_id in possible_rooms:
                possible_rooms.remove(shared.room_id)

        self.last_room = self.room
        self.room = random.choice(possible_rooms)

        if self.room == shared.room_id:
            chosen_diff = possible_diffs[possible_rooms.index(self.room)]
            shared.monster.align_pos_with_door(diffs[chosen_diff])

    def update(self):
        print(self.room)
        if self.must_align:
            if self.align_timer.tick():
                shared.monster.align_pos_with_door(shared.next_door)
                self.room = shared.room_id
                self.must_align = False
            return

        if self.room == shared.room_id:
            shared.monster.update()
            return
        self.change_room()

    def draw(self):
        if self.room == shared.room_id:
            shared.monster.draw()
