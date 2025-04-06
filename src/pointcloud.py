from dataclasses import dataclass
from open3d import geometry


@dataclass
class Pointcloud:
    name: str
    points: geometry.PointCloud
    visibility: bool = True

    def set_visibility(self, visibility: bool):
        self.visibility = visibility
