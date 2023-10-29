from enum import Enum, auto


class MovementType(Enum):
    FIXED = auto()
    STATIC = auto()
    PUSHED = auto()
    CONTROLLED = auto()


class DoorDirection:
    NORTH = auto()
    EAST = auto()
    WEST = auto()
    SOUTH = auto()
