import os
import pyvista as pv
from model.pointcloud import Pointcloud
from model.filter import Filter


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

    # POINTCLOUDS
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

    def get_pointcloud_by_name(self, name) -> Pointcloud | None:
        for pointcloud in self.pointclouds_list:
            if pointcloud.name == name:
                return pointcloud

        return None

    def get_pointclouds(self):
        return self.pointclouds_list

    # FILTERS
    def add_filter(self, name, bounds, color):  # TODO Manage the name
        box = pv.Box(bounds=bounds)
        self.filters_list.append(Filter(name, box, color))

        return box

    def delete_filter(self, name):
        for filter in self.filters_list:
            if filter.name == name:
                self.filters_list.remove(filter)
                break

    def rename_filter(self, old_name, new_name):
        for filter in self.filters_list:
            if filter.name == old_name:
                filter.name = new_name
                break

    def is_filter_name_available(self, name):
        return all(filter.name != name for filter in self.filters_list)

    def set_filter_name(self, old_name, new_name):
        for filter in self.filters_list:
            if filter.name == old_name:
                filter.name = new_name
                break

    def get_filter_by_name(self, name) -> Filter | None:
        for filter in self.filters_list:
            if filter.name == name:
                return filter

        return None

    def set_filter_bounds(self, name, bounds):
        for filter in self.filters_list:
            if filter.name == name:
                box = pv.Box(bounds=bounds)
                filter.box = box
                return box

        return None

    def set_filter_color(self, name, color):
        for filter in self.filters_list:
            if filter.name == name:
                filter.color = color
                break

    def get_filters(self):
        return self.filters_list

    # UTILITY
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
