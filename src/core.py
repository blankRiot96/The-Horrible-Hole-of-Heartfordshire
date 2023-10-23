import asyncio

import pygame


class Core:
    def __init__(self) -> None:
        self.win_init()

        self.dt = 0.0
        self.events = []

    def win_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 600))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Title")

    def update(self):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                raise SystemExit

        self.dt = self.clock.tick() / 1000
        self.dt = min(self.dt, 0.1)
        pygame.display.flip()

    def draw(self):
        self.screen.fill(("black"))

    async def run(self):
        while True:
            self.update()
            self.draw()
            await asyncio.sleep(0)
