import os
from pointcloud import Pointcloud


class DataManager:
    def __init__(self):
        self.pointclouds = []
        self.filters = []

    def add_pointcloud(self, filename, pointcloud):
        pointcloud_name = self.extract_name(filename)

        count = sum(
            1 for pointcloud in self.pointclouds if pointcloud_name in pointcloud.name
        )

        if count > 0:
            pointcloud_name = f"{pointcloud_name}_{count}"

        self.pointclouds.append(Pointcloud(pointcloud_name, pointcloud))

        return pointcloud_name

    def remove_pointcloud(self, name):
        for pointcloud in self.pointclouds:
            if pointcloud.name == name:
                self.pointclouds.remove(pointcloud)
                return

        raise ValueError(f"Pointcloud '{name}' not found.")

    def set_visibility(self, name, visible):
        for pointcloud in self.pointclouds:
            if pointcloud.name == name:
                pointcloud.set_visibility(visible)
                return

        raise ValueError(f"Pointcloud '{name}' not found.")

    def is_visible(self, name):
        for pointcloud in self.pointclouds:
            if pointcloud.name == name:
                return pointcloud.visibility

        raise ValueError(f"Pointcloud '{name}' not found.")

    def get_pointcloud(self, name):
        for pointcloud in self.pointclouds:
            if pointcloud.name == name:
                return pointcloud.points

        raise ValueError(f"Pointcloud '{name}' not found.")

    def extract_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]
