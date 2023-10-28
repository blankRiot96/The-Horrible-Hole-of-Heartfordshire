import asyncio

import pygame

from . import shared
from .gamestate import GameStateManager
from .playstate import PlayState


class Core:
    def __init__(self) -> None:
        self.win_init()

        shared.dt = 0.0
        shared.events = []

        play_state = PlayState()
        GameStateManager().add_state(play_state)
        GameStateManager().set_state("PlayState")

    def win_init(self):
        pygame.init()
        shared.screen = pygame.display.set_mode(shared.WIN_SIZE)
        shared.camera_pos = pygame.Vector2(shared.screen.get_rect().center)
        shared.clock = pygame.time.Clock()
        pygame.display.set_caption("Title")

    def update(self):
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

    def draw(self):
        shared.screen.fill((150, 150, 150))
        GameStateManager().draw()
        pygame.display.flip()

    async def run(self):
        while True:
            self.update()
            self.draw()
            await asyncio.sleep(0)
