from enum import Enum, auto


class MovementType(Enum):
    FIXED = auto()
    STATIC = auto()
    PUSHED = auto()
    CONTROLLED = auto()


class DoorDirection(Enum):
    NORTH = (0, 1)
    EAST = (-1, 0)
    WEST = (1, 0)
    SOUTH = (0, -1)
