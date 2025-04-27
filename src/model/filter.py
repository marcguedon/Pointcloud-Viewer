import pyvista as pv
from dataclasses import dataclass
from pyvista import PolyData


@dataclass
class Filter:
    _name: str
    _box: PolyData
    _color: str

    def __init__(
        self,
        name: str,
        box: PolyData | tuple[float, float, float, float, float, float],
        color: str,
    ):
        self.name = name
        self.box = box
        self.color = color

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
    def box(self, box: PolyData | tuple[float, float, float, float, float, float]):
        if isinstance(box, PolyData):
            self._box = box
        else:
            self._box = pv.Box(bounds=box)

    @color.setter
    def color(self, color: str):
        self._color = color
