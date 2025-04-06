from dataclasses import dataclass


@dataclass
class PointcloudFilter:
    name: str
    z_min: float
    z_max: float

    def set_z_min(self, z_min: float):
        self.z_min = z_min

    def set_z_max(self, z_max: float):
        self.z_max = z_max
