import asyncio

import pygame

from . import shared
from .gamestate import GameStateManager


class Core:
    def __init__(self) -> None:
        self.win_init()

        shared.dt = 0.0
        shared.events = []

        from .introstate import IntroState
        from .playstate import PlayState

        GameStateManager().add_state(PlayState)
        GameStateManager().add_state(IntroState)
        GameStateManager().set_state("IntroState")

    def win_init(self) -> None:
        pygame.init()
        shared.screen = pygame.display.set_mode(shared.WIN_SIZE)
        shared.clock = pygame.time.Clock()
        pygame.display.set_caption("Title")

    def update(self) -> None:
        shared.events = pygame.event.get()
        for event in shared.events:
            if event.type == pygame.QUIT:
                raise SystemExit

        GameStateManager().handle_events()

        shared.dt = shared.clock.tick() / 1000
        shared.dt = min(shared.dt, 0.1)

        shared.keys = pygame.key.get_pressed()
        shared.mouse_pos = pygame.mouse.get_pos()

        GameStateManager().update()

    def draw(self) -> None:
        shared.screen.fill("black")
        GameStateManager().draw()
        pygame.display.flip()

    async def run(self) -> None:
        while True:
            self.update()
            self.draw()
            await asyncio.sleep(0)
