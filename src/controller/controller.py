import os
import pyvista as pv
from model.pointcloud import Pointcloud


class Controller:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Controller, cls).__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        self.pointclouds_list = []
        self.filters_list = []

    def load_pointcloud(self, path):
        name = self.get_name_from_path(path)
        pointcloud_data = pv.read(path)

        self.pointclouds_list.append(Pointcloud(name, pointcloud_data))

        return name, pointcloud_data

    def delete_pointcloud(self, name):
        for pointcloud in self.pointclouds_list:
            if pointcloud.name == name:
                self.pointclouds_list.remove(pointcloud)
                break

    def rename_pointcloud(self, old_name, new_name):
        for pointcloud in self.pointclouds_list:
            if pointcloud.name == old_name:
                pointcloud.name = new_name
                break

    def is_pointcloud_name_available(self, name):
        return all(pointcloud.name != name for pointcloud in self.pointclouds_list)

    def set_pointcloud_name(self, old_name, new_name):
        for pointcloud in self.pointclouds_list:
            if pointcloud.name == old_name:
                pointcloud.name = new_name
                break

    def get_pointcloud_by_name(self, name):
        for pointcloud in self.pointclouds_list:
            if pointcloud.name == name:
                return pointcloud
        return None

    def get_name_from_path(self, path):
        filename = self.extract_name(path)

        existing_names = {pointcloud.name for pointcloud in self.pointclouds_list}
        original_filename = filename
        count = 1

        while filename in existing_names:
            filename = f"{original_filename}_{count}"
            count += 1

        return filename

    def extract_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]
