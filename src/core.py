import asyncio

import pygame


class Core:
    def __init__(self) -> None:
        self.win_init()

        self.shared.dt = 0.0
        self.shared.mouse_pos = (0, 0)

    def win_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 600))
        self.shared.screen = self.screen
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Title")

    def update(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                raise SystemExit

        self.state_manager.update()
        self.shared.dt = self.clock.tick() / 1000
        self.shared.dt = min(self.shared.dt, 0.1)
        self.shared.mouse_pos = pygame.mouse.get_pos()
        pygame.display.flip()

    def draw(self):
        self.screen.fill(("black"))
        self.state_manager.draw()

    async def run(self):
        while True:
            self.update()
            self.draw()
            await asyncio.sleep(0)
