from collections import defaultdict, deque

from . import shared
from ._types import Coordinate
from .enums import MovementType


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

    @staticmethod
    def get_neighbors(cell: Coordinate) -> list[Coordinate]:
        neighbors: list[Coordinate] = []
        # (y, x)
        offsets = [(0, 1), (1, 0), (-1, 0), (0, -1)]
        for offset in offsets:
            test_coord = (cell[0] + offset[0], cell[1] + offset[1])
            if 0 <= test_coord[0] < shared.rows and 0 <= test_coord[1] < shared.cols:
                neighbors.append(test_coord)

        return neighbors

    @staticmethod
    def get_walkable_cells() -> set[Coordinate]:
        cells: set[Coordinate] = set()

        for entity in shared.entities:
            cell = int(entity.cell.x), int(entity.cell.y)
            if entity.movement_type in [
                MovementType.HOLE,
                MovementType.PUSHED,
                MovementType.STATIC,
            ]:
                if cell in cells:
                    cells.remove(cell)
            else:
                cells.add(cell)

        return cells

    def create_graph(self) -> None:
        walkable_cells = self.get_walkable_cells()

        for cell in walkable_cells:
            neighbors = self.get_neighbors(cell)
            for neighbor in neighbors:
                if neighbor in walkable_cells:
                    self.add_connection(cell, neighbor)

    # def search(self, source: Coordinate, dest: Coordinate) -> deque[Coordinate]:
    #     output: deque[Coordinate] = deque()

    #     explored: list[Coordinate] = [source]
    #     parents: dict[Coordinate, Coordinate] = {}
    #     nodes: deque[Coordinate] = deque()
    #     nodes.append(source)

    #     while len(nodes) > 0:
    #         node = nodes.popleft()

    #         if node == dest:
    #             nodes.clear()

    #         for neighbor in self.get_neighbors(node):
    #             if neighbor not in explored:
    #                 explored.append(neighbor)
    #                 parents[neighbor] = node
    #                 nodes.append(neighbor)

    #     current_node = dest
    #     while current_node != source:
    #         output.appendleft(current_node)
    #         try:
    #             # TODO: Find source of issues
    #             current_node = parents[current_node]
    #         except IndexError:
    #             continue
    #     output.appendleft(source)

    #     return output

    def search(self, source: Coordinate, dest: Coordinate) -> deque[Coordinate]:
        output: deque[Coordinate] = deque()

        explored: set[Coordinate] = set()
        parents: dict[Coordinate, Coordinate] = {}
        nodes: deque[Coordinate] = deque([source])

        while nodes:
            node = nodes.popleft()

            if node == dest:
                break

            for neighbor in self.get_neighbors(node):
                if neighbor not in explored:
                    explored.add(neighbor)
                    parents[neighbor] = node
                    nodes.append(neighbor)

        current_node = dest
        while current_node != source:
            output.appendleft(current_node)
            try:
                current_node = parents[current_node]
            except KeyError:
                continue
        output.appendleft(source)

        return output
