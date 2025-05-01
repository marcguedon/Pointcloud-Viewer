from dataclasses import dataclass
from pyvista import PolyData


@dataclass
class Pointcloud:
    _name: str
    _points: PolyData

    @property
    def name(self) -> str:
        return self._name

    @property
    def points(self) -> PolyData:
        return self._points

    @name.setter
    def name(self, name: str):
        self._name = name

    @points.setter
    def points(self, points: PolyData):
        self._points = points
