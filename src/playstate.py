from .entities import Player, Stone
from .gamestate import GameState
from .grid import Grid


class PlayState(GameState):
    def __init__(self) -> None:
        super().__init__("PlayState")
        self.grid = Grid()
        self.grid.add_entity(Player((3, 4)))
        self.grid.add_entity(Stone((4, 6)))

    def handle_events(self) -> None:
        ...

    def update(self):
        self.grid.update()

    def draw(self):
        self.grid.draw()
