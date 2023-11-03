import pygame

from . import shared
from .asset_loader import Loader
from .common import render_at


class CombinationLock:
    """Handles the riddle rendering for the combination lock puzzle"""

    def __init__(self) -> None:
        self.font = Loader().get_font(
            shared.ASSETS_PATH / "font/DotGothic16-Regular.ttf", 24
        )
        self.riddle = "This creature dwelves in the sea.. it has stretchy arms and its\
 name starts with the word in room 8.. light the first and nth torch where\
 n is the number of arms this sea creature has."
        self.image = self.font.render(
            self.riddle,
            True,
            "white",
            wraplength=int(shared.WIN_WIDTH / 2),
            bgcolor="black",
        )

    def update(self):
        ...

    def draw(self):
        if shared.room_id != 4:
            return
        render_at(shared.screen, self.image, "midbottom", offset=(0, -50))
