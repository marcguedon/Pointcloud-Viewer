import os
import pyvista as pv


class PointcloudService:
    def __init__(self):
        pass

    def get_pointcloud_data_from_path(self, pointcloud_list, path):
        name = self.get_pointcloud_name_from_path(pointcloud_list, path)
        pointcloud_data = pv.read(path)

        return name, pointcloud_data

    def get_pointcloud_name_from_path(self, pointclouds_list, path):
        name = self.extract_name(path)

        existing_names = {pointcloud.name for pointcloud in pointclouds_list}
        original_filename = name
        count = 1

        while name in existing_names:
            name = f"{original_filename}_{count}"
            count += 1

        return name

    def extract_name(self, path):
        return os.path.splitext(os.path.basename(path))[0]
