from __future__ import annotations

from abc import ABC, abstractmethod


class GameState(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def handle_events(self) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def draw(self) -> None:
        pass


class GameStateManager:
    __instance = None
    __initialized = False

    def __new__(cls) -> GameStateManager:
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self) -> None:
        if not GameStateManager.__initialized:
            self.states: dict[str, type] = {}
            self.state: GameState | None = None
            GameStateManager.__initialized = True

    def reset(self) -> None:
        GameStateManager.__initialized = False
        GameStateManager.__instance = None

    def add_state(self, state: type) -> None:
        self.states[state.__name__] = state

    def set_state(self, name: str) -> None:
        self.state = self.states[name]()

    def update(self) -> None:
        if self.state is not None:
            self.state.update()

    def draw(self) -> None:
        if self.state is not None:
            self.state.draw()

    def handle_events(self) -> None:
        if self.state is not None:
            self.state.handle_events()
