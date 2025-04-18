from dataclasses import dataclass
from pyvista import DataSet


@dataclass
class Pointcloud:
    _name: str
    _points: DataSet

    @property
    def name(self) -> str:
        return self._name

    @property
    def points(self) -> DataSet:
        return self._points

    @name.setter
    def name(self, name: str):
        self._name = name

    @points.setter
    def points(self, points: DataSet):
        self._points = points
