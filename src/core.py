import asyncio

import pygame

from . import shared
from .enums import DoorDirection
from .gamestate import GameStateManager


class Core:
    def __init__(self) -> None:
        self.win_init()

        shared.dt = 0.0
        shared.events = []

        from .deathscreen import DeathScreen
        from .introstate import IntroState
        from .mainmenu import MainMenu
        from .playstate import PlayState

        GameStateManager().add_state(PlayState)
        GameStateManager().add_state(IntroState)
        GameStateManager().add_state(MainMenu)
        GameStateManager().add_state(DeathScreen)

        GameStateManager().set_state("IntroState")

    def reset(self) -> None:
        shared.room_id = 1
        shared.entities_in_room = {}
        shared.next_door = DoorDirection.SOUTH
        shared.update_graph = True
        if hasattr(shared, "overlay"):
            del shared.player
            del shared.monster
        GameStateManager().reset()
        self.__init__()
        GameStateManager().set_state("PlayState")

    def win_init(self) -> None:
        pygame.init()
        shared.screen = pygame.display.set_mode(shared.WIN_SIZE)
        shared.clock = pygame.time.Clock()
        pygame.display.set_caption(shared.game_name)

    def update(self) -> None:
        if shared.reset:
            self.reset()
            shared.reset = False

        shared.events = pygame.event.get()
        for event in shared.events:
            if event.type == pygame.QUIT:
                raise SystemExit

        GameStateManager().handle_events()
        if shared.reset:
            return

        shared.dt = shared.clock.tick() / 1000
        shared.dt = min(shared.dt, 0.1)

        shared.keys = pygame.key.get_pressed()
        shared.mouse_pos = pygame.mouse.get_pos()

        GameStateManager().update()
        pygame.display.set_caption(f"{shared.clock.get_fps():.0f}")

    def draw(self) -> None:
        shared.screen.fill("black")
        GameStateManager().draw()
        pygame.display.flip()

    async def run(self) -> None:
        while True:
            self.update()
            self.draw()
            await asyncio.sleep(0)
