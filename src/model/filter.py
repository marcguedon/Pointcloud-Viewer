from dataclasses import dataclass
from pyvista import PolyData


@dataclass
class Filter:
    _name: str
    _box: PolyData
    _color: str

    @property
    def name(self) -> str:
        return self._name

    @property
    def box(self) -> PolyData:
        return self._box

    @property
    def color(self) -> str:
        return self._color

    @name.setter
    def name(self, name: str):
        self._name = name

    @box.setter
    def box(self, box: PolyData):
        self._box = box

    @color.setter
    def color(self, color: str):
        self._color = color
