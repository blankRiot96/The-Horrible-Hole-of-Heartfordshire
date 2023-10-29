from collections import defaultdict

from ._types import Coordinate


class Graph:
    def __init__(self) -> None:
        self._graph: dict[Coordinate, set[Coordinate]] = defaultdict(set)

    def add_connection(self, first_end: Coordinate, second_end: Coordinate) -> None:
        self._graph[first_end].add(second_end)
        self._graph[second_end].add(first_end)

    def add_connections(self, connections: list[tuple[Coordinate, Coordinate]]) -> None:
        for cxn in connections:
            self.add_connection(*cxn)

    def remove_connection(self, first_end: Coordinate, second_end: Coordinate) -> None:
        if self.is_connected(first_end, second_end):
            self._graph[first_end].remove(second_end)
            self._graph[second_end].remove(first_end)

    def remove_connections(
        self, connections: list[tuple[Coordinate, Coordinate]]
    ) -> None:
        for cxn in connections:
            self.remove_connection(*cxn)

    def get_connected_nodes(self, node: Coordinate) -> set[Coordinate]:
        return self._graph[node]

    def is_connected(self, first_end: Coordinate, second_end: Coordinate) -> bool:
        return second_end in self._graph[first_end]

    def remove_node(self, node: Coordinate) -> None:
        for connected_node in self.get_connected_nodes(node):
            self.remove_connection(node, connected_node)
        del self._graph[node]
