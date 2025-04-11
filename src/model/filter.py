from dataclasses import dataclass


@dataclass
class Filter:
    _name: str
    _color: str
    _x_min: float
    _x_max: float
    _y_min: float
    _y_max: float
    _z_min: float
    _z_max: float

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
