from enum import Enum, auto


class MovementType(Enum):
    # FIXED -> movement path
    FIXED = auto()
    # STATIC -> background things that don't move
    STATIC = auto()
    # PUSHED -> Things the player can push
    PUSHED = auto()
    # CONTROLLED -> player
    CONTROLLED = auto()
    # FOREGROUND -> foreground things
    FOREGROUND = auto()
    # HOLE -> holes. player can't walk over, but stones can be pushed over
    HOLE = auto()
    # PATHING -> can pathfind
    PATHING = auto()


class DoorDirection(Enum):
    # The values indicate the direction in which the player needs to move towards
    # if entering from the respective NEWS door
    # So if you enter from east gate, you want to move towards the left/west
    NORTH = (0, 1)
    EAST = (-1, 0)
    WEST = (1, 0)
    SOUTH = (0, -1)


class StoneSymbol(Enum):
    TEACUP = auto()
    SWITZERLAND = auto()
    PIRATE = auto()
    WALES = auto()
    IRELAND = auto()
